import base64
from datetime import datetime

import cv2
import numpy as np
from PIL import Image
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from id_capture.forms.signinForm import SigninForm
from id_capture.forms.studentform import StudentForm
from id_capture.models import FaceImage, Student
from id_capture.ultility import image_preprocessing, face_count_check, send_file_data


def home(request):
    return render(request, "id_capture/home.html")


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


@login_required(redirect_field_name='', login_url=None)
def login_face_recognition_check(request):
    if request.user.face_image:
        return HttpResponseRedirect(reverse('student_face_recognition'))
    else:
        return render(request, "login/recognition_check.html")


# @login_required
def login_student_recognition(request):
    if request.method == 'POST':
        fs = request.FILES['snap']
        if fs:
            img = cv2.imdecode(np.frombuffer(fs.read(), np.uint8), cv2.IMREAD_UNCHANGED)
            # print('Shape:', img.shape)
            # rectangle(image, start_point, end_point, color, thickness)
            img = cv2.rectangle(img, (20, 20), (300, 220), (0, 0, 255), 2)

            text = datetime.now().strftime('%Y.%m.%d %H.%M.%S.%f')
            img = cv2.putText(img, text, (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            # cv2.imshow('image', img)
            # cv2.waitKey(1)

            # https://jdhao.github.io/2019/07/06/python_opencv_pil_image_to_bytes/
            ret, buf = cv2.imencode('.jpg', img)
            b64 = base64.b64encode(buf)

            # return f'Got Snap! {img.shape}'
            return send_file_data(b64)
        return JsonResponse({'hello': 'world'})
        # return JsonResponse({'status': 0})
    return render(request, 'login/facial_recognition.html')


def instruction(request):
    return render(request, "id_capture/instruction.html")


def register_form(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student_info = ""
            student = form.save(commit=False)
            clearPassNoHash = form.cleaned_data['password']
            student.set_password(clearPassNoHash)
            for key in form:
                if 'id_image' in key.name or 'gender' in key.name or 'password' in key.name:
                    continue
                student_info = student_info + str(key.value()) + " "

            if image_preprocessing(request.FILES['id_image'], student_info) > 70:
                student.save()

                user = authenticate(request, id=student.id, password=student.password)
                login(request, user)
                return redirect('facial_capture')
    else:
        form = StudentForm()

    return render(request, 'id_capture/info_register.html', {'form': form})


@login_required
def facial_capture(request):
    if request.method == 'POST':
        fs = request.FILES['snap']
        if fs:
            if face_count_check(Image.open(fs)):
                student = Student.objects.get(id=request.session['id'])
                if student:
                    FaceImage.objects.create(student=student, image=fs)
                    messages.success(request=request, message='Signup successfully.')
                    student.face_image = True
                    student.save()
                    return JsonResponse({"status": 1})
            messages.error(request=request,
                           message='Invalid snap. Please make sure there are only one person in the picture.')
            return JsonResponse({'status': 0})
        messages.debug(request=request, message='Image not posted.')
        return JsonResponse({'status': 0})
    return render(request, 'id_capture/facial_capture.html')


@login_required(redirect_field_name='', login_url=None)
def logout_student(request):
    logout(request)
    return redirect('home')