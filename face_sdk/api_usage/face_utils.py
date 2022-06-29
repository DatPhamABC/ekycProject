import numpy as np


import yaml

from face_sdk.core.image_cropper.arcface_cropper.FaceRecImageCropper import FaceRecImageCropper
from face_sdk.core.model_handler.face_alignment.FaceAlignModelHandler import FaceAlignModelHandler
from face_sdk.core.model_handler.face_detection.FaceDetModelHandler import FaceDetModelHandler
from face_sdk.core.model_handler.face_recognition.FaceRecModelHandler import FaceRecModelHandler
from face_sdk.core.model_loader.face_alignment.FaceAlignModelLoader import FaceAlignModelLoader
from face_sdk.core.model_loader.face_detection.FaceDetModelLoader import FaceDetModelLoader
from face_sdk.core.model_loader.face_recognition.FaceRecModelLoader import FaceRecModelLoader

with open('face_sdk/config/model_conf.yaml') as f:
    model_conf = yaml.load(f, Loader=yaml.FullLoader)


def face_detection(image):
    """
        :param image: image in bgr color
        :type image: cv2 image
        :returns: list of bounding box(es) of face(s)
        :rtype:
    """
    # common setting for all model, need not modify.
    model_path = "face_sdk\\models\\"

    # model setting, modified along with model
    scene = 'non-mask'
    model_category = 'face_detection'
    model_name = model_conf[scene][model_category]

    # load model
    try:
        faceDetModelLoader = FaceDetModelLoader(model_path, model_category, model_name)
    except Exception as e:
        raise

    try:
        model, cfg = faceDetModelLoader.load_model()
    except Exception as e:
        raise

    # read image (bgr)
    faceDetModelHandler = FaceDetModelHandler(model, 'cpu', cfg)

    try:
        dets = faceDetModelHandler.inference_on_image(image)
    except Exception as e:
        raise

    return dets


def face_recognition(saved_image, stream_image):
    """
        :param saved_image: image saved in databse in bgr color
        :type saved_image: cv2 image
        :param stream_image: image from camera in bgr color
        :type stream_image: cv2 image
        :returns: score comparing face feature in 2 images
        :rtype: float
    """
    # common setting for all models, need not modify.
    model_path = 'face_sdk\\models\\'
    scene = 'non-mask'

    # face landmark model setting.
    model_category = 'face_alignment'
    model_name = model_conf[scene][model_category]
    try:
        faceAlignModelLoader = FaceAlignModelLoader(model_path, model_category, model_name)
        model, cfg = faceAlignModelLoader.load_model()
        faceAlignModelHandler = FaceAlignModelHandler(model, 'cpu', cfg)
    except Exception as e:
        raise

    # face recognition model setting.
    model_category = 'face_recognition'
    model_name = model_conf[scene][model_category]
    try:
        faceRecModelLoader = FaceRecModelLoader(model_path, model_category, model_name)
        model, cfg = faceRecModelLoader.load_model()
        model = model.module.cpu()
        faceRecModelHandler = FaceRecModelHandler(model, 'cpu', cfg)
    except Exception as e:
        raise

    # read image and get face features.
    face_cropper = FaceRecImageCropper()
    try:
        dets = face_detection(saved_image)
        face_nums = dets.shape[0]
        if face_nums != 1:
            raise 'Input image should only contain one faces to compute similarity!'
        landmarks = faceAlignModelHandler.inference_on_image(saved_image, dets[0])

        landmarks_list = []
        for (x, y) in landmarks.astype(np.int32):
            landmarks_list.extend((x, y))
        cropped_image = face_cropper.crop_image_by_mat(saved_image, landmarks_list)
        saved_feature = faceRecModelHandler.inference_on_image(cropped_image)

        dets = face_detection(stream_image)
        face_nums = dets.shape[0]
        print(face_nums)
        if face_nums == 1:
            landmarks = faceAlignModelHandler.inference_on_image(stream_image, dets[0])

            landmarks_list = []
            for (x, y) in landmarks.astype(np.int32):
                landmarks_list.extend((x, y))
            cropped_image = face_cropper.crop_image_by_mat(stream_image, landmarks_list)
            stream_feature = faceRecModelHandler.inference_on_image(cropped_image)

            score = np.dot(saved_feature, stream_feature)
            print('score: ' + str(score))
            return score
        return -1
    except Exception as e:
        raise e
