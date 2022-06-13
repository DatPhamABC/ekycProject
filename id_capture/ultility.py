import re
import string

import cv2
import face_recognition
from django.http import HttpResponse
from thefuzz import fuzz
import numpy as np
from paddleocr import PaddleOCR


# def image_preprocessing(image, student_info):
#     image = cv2.imdecode(np.fromstring(image.read(), np.uint8), cv2.IMREAD_COLOR)
#     gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#
#     thresh, im_bw = cv2.threshold(gray_image, 150, 160, cv2.THRESH_BINARY)
#
#     ## Border remove
#     # no_borders = remove_borders(no_noise)
#
#     # pytesseract.pytesseract.tesseract_cmd = 'E:\\Program\\TesseractOCR\\tesseract.exe'
#     # reader = easyocr.Reader(['vi'])
#     # result = reader.readtext(no_borders)
#     # result = pytesseract.image_to_string(gray_image, lang="vie")
#     # result = str(result).replace(":", " ").lower()
#     # concat_string = ""
#     # for i in result:
#     #     concat_string = concat_string + i[1] + " "
#
#     # paddle ocr
#     paddle_ocr = PaddleOCR(lang='eng')
#     ocr_result = paddle_ocr.ocr(im_bw, cls=True)
#     result = ""
#     for line in ocr_result:
#         print(line)
#         result = result + line[1][0] + " "
#     print(result)
#
#     # return fuzz.ratio(concat_string, student_info)*fuzz.ratio(student_info, concat_string)/100
#     print(fuzz.ratio(student_info, result))
#     print(fuzz.ratio(result, student_info))
#     print(fuzz.partial_ratio(result, student_info))
#     print(fuzz.token_sort_ratio(result, student_info))
#     print(fuzz.token_set_ratio(result, student_info))
#     return fuzz.token_set_ratio(student_info, result)


def face_count_check(img):
    """
    Check if there is only one person in the image
    :param img: as InMemoryUploadedFile
    :return: Boolean
    """
    face_location = face_recognition.face_locations(np.asarray(img))
    if len(face_location) == 1:
        return True
    return False


def send_file_data(data, mimetype='image/jpeg', filename='output.jpg'):
    response = HttpResponse(data, content_type=mimetype)
    response['Content-Disposition'] = 'attachment; filename={}'.format(filename)
    return response


def face_recog(registered_image, cam_feed):
    registered_encoding = face_recognition.face_encodings(registered_image)[0]

    cam_encoding = face_recognition.face_encodings(cam_feed)[0]
    results = face_recognition.compare_faces([registered_encoding], cam_encoding)

    return results[0]


def prepare_image(cvImage):

    def get_sub_image(rect, img):
        # Get center, size, and angle from rect
        center, size, theta = rect
        size = tuple(reversed(size))

        # Convert to int
        center, size = tuple(map(int, center)), tuple(map(int, size))

        # Get rotation matrix for rectangle
        M = cv2.getRotationMatrix2D(center, theta + 90, -1)

        # Perform rotation on src image
        dst = cv2.warpAffine(img, M, img.shape[:2])
        out = cv2.getRectSubPix(dst, size, center)
        return out

    # Convert request to cv2 image
    newImage = cv2.imdecode(np.fromstring(cvImage.read(), np.uint8), cv2.IMREAD_COLOR)

    # Prep image (copy, convert to hsv, h and threshold)
    hsv = cv2.cvtColor(newImage, cv2.COLOR_RGB2HSV)
    h, s, v = cv2.split(hsv)
    ret, thresh = cv2.threshold(h, 50, 255, cv2.THRESH_OTSU)

    # Find all contours and sort from smallest to largest
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea)

    # Find largest contour and  min area rectangle
    largestContour = contours[-1]
    minAreaRect = cv2.minAreaRect(largestContour)

    # Rotate and cut image
    out = get_sub_image(minAreaRect, newImage)
    return out


def get_ocr_result(image):
    # Preparing image (deskew, crop)
    prep = preparing_image(image)

    # Convert image to grayscale
    gray = cv2.cvtColor(prep, cv2.COLOR_BGR2GRAY)

    # Put into PaddleOCR
    paddle_ocr = PaddleOCR(lang='eng')
    ocr_result = paddle_ocr.ocr(gray, cls=True)
    print(ocr_result)


def prepare_ocr_result(image, ocr_result):
    def centroid_propotion(points, width, length):
        x = [p[0] for p in points]
        y = [p[1] for p in points]
        centroid = [round((sum(x) / len(points)) * 100 / length, 2), round((sum(y) / len(points)) * 100 / width, 2)]
        return centroid

    def get_centroid_list(ocr_result, width, length):
        centroid_list = []
        for line in ocr_result:
            centroid_list.append(centroid_propotion(line[0], width, length))
        return centroid_list

    def find_info(card_info_list, centroid_list, ocr_result):
        delta = 2
        card_result = {
            'id': '',
            'name': '',
            'date_of_birth': '',
            'gender': '',
            'class_year': '',
            'major': ''
        }

        try:
            for k in range(len(centroid_list)):
                i = 0
                if len(card_info_list) == 0:
                    break
                while i < len(card_info_list):
                    if abs(card_info_list[i][1][0] - centroid_list[k][0]) < delta \
                            and abs(card_info_list[i][1][1] - centroid_list[k][1]) < delta:
                        card_result[card_info_list[i][0]] = ocr_result[k][1][0]
                        card_info_list.pop(i)
                        break
                    i += 1
        except IndexError:
            pass
        return card_result

    def correct_info(card_result):
        card_result['name'] = card_result['name'].split(':', 1)[-1]\
            .lower().replace('ho va ten', '')\
            .replace('hovaten', '')\
            .replace('ho vaten', '')\
            .replace('hova ten', '')\
            .strip(string.punctuation)\
            .capitalize()

        card_result['id'] = re.sub('[^09]', '', card_result['id'])

        card_result['date_of_birth'] = card_result['date_of_birth'].split(':', 1)[-1]\
            .lower().replace('ngaysinh', '')\
            .replace('ngay sinh', '')\
            .strip(string.punctuation)

        card_result['gender'] = card_result['gender'].split(':', 1)[-1]\
            .lower().replace('gioi tinh', '')\
            .replace('gioitinh', '')\
            .strip(string.punctuation)

        card_result['class_year'] = card_result['class_year'].split(':', 1)[-1]\
            .lower().replace('khoa hoc', '')\
            .replace('khoahoc', '')\
            .strip(string.punctuation)\
            .upper()

        card_result['major'] = card_result['major'].split(':', 1)[-1]\
            .lower().replace('nganh hoc', '')\
            .replace('nganhhoc', '')\
            .strip(string.punctuation)
        return card_result

    card_info_list = [
        ['name', [49.17, 43.35]],
        ['date_of_birth', [43.41, 51.23]],
        ['gender', [86.27, 51.69]],
        ['class_year', [46.09, 59.33]],
        ['major', [51.51, 67.15]],
        ['id', [13.6, 72.36]]
    ]

    width, length = image.shape
    centroid_list = get_centroid_list(ocr_result, width, length)
    result = find_info(card_info_list, centroid_list, ocr_result)
    corrected_result = correct_info(result)
    return corrected_result


def compare_result(form_info, prepared_ocr_result):
    print(fuzz.ratio(form_info, prepared_ocr_result))
    print(fuzz.ratio(form_info, prepared_ocr_result))
    print(fuzz.partial_ratio(form_info, prepared_ocr_result))
    print(fuzz.token_sort_ratio(form_info, prepared_ocr_result))
    print(fuzz.token_set_ratio(form_info, prepared_ocr_result))
    return fuzz.token_set_ratio(form_info, prepared_ocr_result)
