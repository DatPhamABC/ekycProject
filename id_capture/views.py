import threading

import cv2
from PIL import Image
from django.http import HttpResponseRedirect, StreamingHttpResponse, HttpResponse
from django.shortcuts import render

from id_capture.forms.studentform import StudentForm
from id_capture.models import FaceImage, Student
from id_capture.ultility import image_preprocessing, face_count_check

from django.views.decorators import gzip


def home(request):
    return render(request, "id_capture/home.html")


def login(request):
    return render(request, "id_capture/login.html")


def instruction(request):
    return render(request, "id_capture/instruction.html")


def register_form(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student_info = ""
            for key in form:
                if 'id_image' in key.name or 'gender' in key.name:
                    continue
                if 'id' in key.name:
                    request.session['id'] = key.value()
                student_info = student_info + str(key.value()) + " "
            if image_preprocessing(request.FILES['id_image'], student_info) > 70:
                form.save()
                return HttpResponseRedirect('/signup/facial_capture')
    else:
        form = StudentForm()

    return render(request, 'id_capture/info_register.html', {'form': form})


# @gzip.gzip_page
def facial_capture(request):
    if request.method == 'POST':
        # fs = request.files['snap'] # it raise error when there is no `snap` in form
        print('here')
        fs = request.FILES['snap']
        print(fs)
        print(request.session['id'])
        if fs:
            print('FileStorage:', fs)
            print('filename:', fs.name)
            if face_count_check(Image.open(fs.stream)):
                facial_image = FaceImage(Student.objects.get(id=request.session['id']), fs)
                facial_image.save()
            return HttpResponse('Got Snap!')
        else:
            return HttpResponse('You forgot Snap!')

    return render(request, 'id_capture/facial_capture.html')
    # try:
    #     cam = FacialCapture()
    #     return StreamingHttpResponse(gen(cam), content_type='multipart/x-mixed-replace; boundary=frame')
    # except:
    #     pass
    # return render(request, 'facial_capture.html')


# class FacialCapture(object):
#     def __init__(self):
#         self.video = cv2.VideoCapture(0)
#         self.grabbed, self.frame = self.video.read()
#         threading.Thread(target=self.update, args=()).start()
#
#     def __del__(self):
#         try:
#             self.video.release()
#         except:
#             print('probably there\'s no cap yet :(')
#         cv2.destroyAllWindows()
#
#     def update(self):
#         while True:
#             self.grabbed, self.frame = self.video.read()
#
#     def get_frame(self):
#         image = self.frame
#         _, jpeg_image = cv2.imencode('.jpeg', image)
#         return jpeg_image.tobytes()
#
#
# def gen(camera):
#     while True:
#         frame = camera.get_frame()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')