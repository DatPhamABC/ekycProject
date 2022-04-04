import cv2
import face_recognition
import pytesseract
from thefuzz import fuzz
import numpy as np


def image_preprocessing(image, student_info):
    image = cv2.imdecode(np.fromstring(image.read(), np.uint8), cv2.IMREAD_COLOR)
    print(type(image))
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # thresh, im_bw = cv2.threshold(gray_image, 150, 160, cv2.THRESH_BINARY)

    # no_noise = noise_removal(im_bw)

    ## Border remove
    # no_borders = remove_borders(no_noise)
    print('here')

    pytesseract.pytesseract.tesseract_cmd = 'E:\\Program\\TesseractOCR\\tesseract.exe'
    # reader = easyocr.Reader(['vi'])
    # result = reader.readtext(no_borders)
    result = pytesseract.image_to_string(gray_image, lang="vie")

    print(student_info)
    print(type(student_info))
    result = str(result).replace(":", " ").lower()
    print(result)
    # concat_string = ""
    # for i in result:
    #     concat_string = concat_string + i[1] + " "

    # print(concat_string)
    # return fuzz.ratio(concat_string, student_info)*fuzz.ratio(student_info, concat_string)/100
    print(fuzz.ratio(student_info, result))
    print(fuzz.ratio(result, student_info))
    print(fuzz.partial_ratio(result, student_info))
    print(fuzz.token_sort_ratio(result, student_info))
    print(fuzz.token_set_ratio(result, student_info))
    return fuzz.token_set_ratio(student_info, result)


def face_count_check(img):
    face_location = face_recognition.face_locations(img)
    if len(face_location) == 1:
        return True
    return False


def noise_removal(img):
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.erode(img, kernel, iterations=1)
    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    img = cv2.medianBlur(img, 3)
    return img


def remove_borders(img):
    contours, heiarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cntsSorted = sorted(contours, key=lambda x: cv2.contourArea(x))
    cnt = cntsSorted[-1]
    x, y, w, h = cv2.boundingRect(cnt)
    crop = img[y:y + h, x:x + w]
    return crop
