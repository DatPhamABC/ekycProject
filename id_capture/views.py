import base64
from datetime import datetime

import cv2
import numpy as np
from PIL import Image
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from id_capture.forms.signinForm import SigninForm
from id_capture.forms.studentform import StudentForm
from id_capture.models import FaceImage, Student, IDCard
from id_capture.ultility import face_count_check, send_file_data, face_recog, prepare_image, get_ocr_result, \
    prepare_ocr_result, compare_result


def home(request):
    return render(request, "signup/home.html")


def login_student(request):
    print('login page')
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

            img = cv2.imdecode(np.frombuffer(fs.read(), np.uint8), cv2.IMREAD_UNCHANGED)
            # img = cv2.rectangle(img, (20, 20), (300, 220), (0, 0, 255), 2)
            #
            # text = datetime.now().strftime('%Y.%m.%d %H.%M.%S.%f')
            # img = cv2.putText(img, text, (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

            # https://jdhao.github.io/2019/07/06/python_opencv_pil_image_to_bytes/
            ret, buf = cv2.imencode('.jpg', img)

            if face_recog(student_image, buf):
                return JsonResponse({'status': 1})
            # b64 = base64.b64encode(buf)

            # return f'Got Snap! {img.shape}'
            # return send_file_data(b64)
            return JsonResponse({'status': 0})
        return JsonResponse({'hello': 'world'})
        # return JsonResponse({'status': 0})
    return render(request, 'login/facial_recognition.html')


def card_register(request):
    if request.method == 'POST':
        img = request.FILES['file-upload-input']
        if img:
            new_image = prepare_image(img)

            print('image sent')
            idcard = IDCard.objects.create(id_card=File(new_image))
            request.session['idcard.id'] = idcard.id
        else:
            print('no image')
    return render(request, 'signup/card_register.html')


def register_form(request):
    idcard_info = None
    if request.session['idcard.id']:
        idcard = IDCard.objects.get(id=request.session['idcard.id'])
        idcard_image = cv2.imread(idcard.id_card.url)
        ocr_result = get_ocr_result(idcard_image)
        idcard_info = prepare_ocr_result(idcard_image, ocr_result)
        print(idcard_info)

    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save(commit=False)
            clearPassNoHash = form.cleaned_data['password']
            student.set_password(clearPassNoHash)
            student_info = student.get_student_info()

            if compare_result(student_info, idcard_info) > 70:
                # student.save()

                # user = authenticate(request, id=student.id, password=student.password)
                # login(request, user)
                print('SUCCESSSSSSSSSSSSSSSSSSS')
                # return redirect('facial_capture')
    else:
        form = StudentForm()

    return render(request, 'signup/info_register.html', {'form': form})


# @login_required(redirect_field_name='', login_url=None)
def facial_capture(request):
    if request.method == 'POST':
        fs = request.FILES['snap']
        if fs:
            if face_count_check(Image.open(fs)):
                # student = request.user
                # if not student.is_anonymous():
                #     FaceImage.objects.create(student=student, image=fs)
                #     messages.success(request=request, message='Signup successfully.')
                #     student.face_image = True
                #     student.save()
                print('image received')
                return JsonResponse({"status": 1})
            messages.error(request=request,
                           message='Invalid snap. Please make sure there are only one person in the picture.')
            return JsonResponse({'status': 0})
        messages.debug(request=request, message='Image not posted.')
        return JsonResponse({'status': 0})
    return render(request, 'signup/facial_capture.html')


@login_required(redirect_field_name='', login_url=None)
def student(request):
    render(request, 'student/student_home.html', {'name': request.user.name})


@login_required(redirect_field_name='', login_url=None)
def logout_student(request):
    logout(request)
    return redirect('home')