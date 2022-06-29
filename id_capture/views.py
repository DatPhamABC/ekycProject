import base64
import uuid
from datetime import datetime

import cv2
import numpy as np
from PIL import Image
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from face_sdk.api_usage.face_utils import face_detection, face_recognition
from id_capture.forms.signinForm import SigninForm
from id_capture.forms.studentform import StudentForm
from id_capture.models import FaceImage, Student, IDCard
from id_capture.utils import face_count_check, send_file_data, face_recog, prepare_image, get_ocr_result, \
    prepare_ocr_result, compare_result


def home(request):
    if request.user.is_authenticated:
        return redirect('student')
    return render(request, "signup/home.html")


def login_student(request):
    if request.user.is_authenticated:
        return redirect('student')
    if request.method == "POST":
        form = SigninForm(request.POST)
        if form.is_valid():
            user = authenticate(request, id=form['id'].value(), password=form['password'].value())
            if user is not None:
                login(request, user)
                return redirect('login_check')
    else:
        form = SigninForm()
    return render(request, "login/login.html", {'form': form})


def instruction(request):
    return render(request, "signup/instruction.html")


@login_required(redirect_field_name='', login_url=None)
def login_face_recognition_check(request):
    if request.user.face_image:
        return HttpResponseRedirect(reverse('student_face_recognition'))
    else:
        return render(request, "login/recognition_check.html")


@login_required(redirect_field_name='', login_url=None)
def login_student_recognition(request):
    if request.method == 'POST':
        fs = request.FILES['snap']
        if fs:
            student_image = FaceImage.objects.get(student=request.user)
            saved_img = cv2.imdecode(np.asarray(bytearray(student_image.image.read())), cv2.IMREAD_UNCHANGED)

            stream_img = cv2.imdecode(np.frombuffer(fs.read(), np.uint8), cv2.IMREAD_UNCHANGED)
            # img = cv2.rectangle(img, (20, 20), (300, 220), (0, 0, 255), 2)
            #
            # text = datetime.now().strftime('%Y.%m.%d %H.%M.%S.%f')
            # img = cv2.putText(img, text, (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

            # https://jdhao.github.io/2019/07/06/python_opencv_pil_image_to_bytes/
            # ret, buf = cv2.imencode('.jpg', img)

            score = face_recognition(saved_img, stream_img)
            if score >= 0.8:
                return JsonResponse({'status': 1})
            elif score < 0:
                return JsonResponse({'status': -1})
            # b64 = base64.b64encode(buf)

            # return f'Got Snap! {img.shape}'
            # return send_file_data(b64)
            return JsonResponse({'status': 0})
        return JsonResponse({'hello': 'world'})
        # return JsonResponse({'status': 0})
    return render(request, 'login/facial_recognition.html')


def card_register(request):
    if request.method == 'POST':
        if 'idcard_info' in request.session:
            del request.session['idcard_info']
        img = request.FILES['file-upload-input']
        if img:
            new_image = prepare_image(img)
            ret, encode_img = cv2.imencode('.png', new_image)
            img_file = ContentFile(encode_img)
            idcard = IDCard.objects.create(id=uuid.uuid4().hex)
            idcard.id_card.save('pic.png', img_file, save=True)
            request.session['idcard.id'] = idcard.id
            return redirect('info_register')
        else:
            raise Exception('Image not received.')
    return render(request, 'signup/card_register.html')


def register_form(request):
    idcard_info = None
    idcard = IDCard.objects.get(id=request.session['idcard.id'])
    if request.session['idcard.id']:
        if 'idcard_info' not in request.session:
            if idcard:
                idcard_image = cv2.imread(str(idcard.id_card.url)[1:])
                ocr_result = get_ocr_result(idcard_image)
                idcard_info = prepare_ocr_result(idcard_image, ocr_result)
                request.session['idcard_info'] = idcard_info
        else:
            idcard_info = request.session['idcard_info']

    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            clearPassNoHash = form.cleaned_data['password']
            student.set_password(clearPassNoHash)
            student_info = ""
            for key in form:
                if 'id_image' in key.name or 'gender' in key.name or 'password' in key.name:
                    continue
                student_info = student_info + str(key.value()) + " "

            idcard_text = str(idcard_info['id']) + ' ' \
                          + str(idcard_info['name']) + ' ' \
                          + str(idcard_info['date_of_birth']) + ' ' \
                          + str(idcard_info['class_year']) + ' ' \
                          + str(idcard_info['major'])

            if compare_result(student_info, idcard_text) > 90:
                if idcard:
                    student.id_image = idcard
                else:
                    raise Exception('No id card image found.')
                student.save()
                user = authenticate(request, id=student.id, password=form['password'].value(),
                                    backend='id_capture.backends.StudentBackend')
                login(request, user, backend='id_capture.backends.StudentBackend')
                return redirect('facial_capture')
    else:
        form = StudentForm(initial={
            'id': idcard_info['id'],
            'name': idcard_info['name'],
            'date_of_birth': idcard_info['date_of_birth'],
            'gender': idcard_info['gender'],
            'class_year': idcard_info['class_year'],
            'major': idcard_info['major']
        })

    return render(request, 'signup/info_register.html', {'form': form})


@login_required(redirect_field_name='', login_url=None)
def facial_capture(request):
    if request.method == 'POST':
        fs = request.FILES['snap']
        if fs:
            img = cv2.imdecode(np.fromstring(fs.read(), np.uint8), cv2.IMREAD_UNCHANGED)
            face_det = face_detection(img)
            if face_det.shape[0] == 1:
                student = request.user
                if student.is_authenticated:
                    FaceImage.objects.create(student=student, image=fs)
                    messages.success(request=request, message='Signup successfully.')
                    student.face_image = True
                    student.save()
                    return JsonResponse({"status": 1})
                raise Exception('User is not authenticated.')
            messages.error(request=request,
                           message='Invalid snap. Please make sure there is exactly one person in the picture.')
            return JsonResponse({'status': 0})
        messages.debug(request=request, message='Image not posted.')
        return JsonResponse({'status': 0})
    return render(request, 'signup/facial_capture.html')


@login_required(redirect_field_name='', login_url=None)
def student(request):
    return render(request, 'student/student_home.html', {'name': request.user.name})


@login_required(redirect_field_name='', login_url=None)
def logout_student(request):
    logout(request)
    return redirect('home')
