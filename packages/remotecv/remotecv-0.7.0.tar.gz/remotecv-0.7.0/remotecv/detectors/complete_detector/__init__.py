#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from remotecv.detectors import CascadeLoaderDetector
from remotecv.detectors.face_detector import FaceDetector
from remotecv.detectors.feature_detector import FeatureDetector

class CompleteDetector(CascadeLoaderDetector):

    def detect(self, image):
        face_detector = FaceDetector()
        feature_detector = FeatureDetector()

        feature_points = []

        face_points = face_detector.detect(image) or []

        if not face_points:
            feature_points = feature_detector.detect(image) or []

        return face_points + feature_points

