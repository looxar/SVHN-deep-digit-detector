#-*- coding: utf-8 -*-

import cv2
import utils
import object_detector.file_io as file_io
import numpy as np
import pickle
import random

class FeatureExtractor():
    
    def __init__(self, descriptor, patch_size, dataset=[]):
        self._desc = descriptor
        self._patch_size = patch_size
        self._dataset = dataset
    
    # Todo : Template Method Pattern??
    def add_positive_sets(self, image_dir, pattern, annotation_path, sample_ratio=1.0, padding=5, augment=True, label=1):
        
        features_set = []
        image_files = self._get_image_files(image_dir, pattern, sample_ratio)
    
        for image_file in image_files:
            image = cv2.imread(image_file)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            image_id = utils.get_file_id(image_file)
            
            annotation_file = "{}/annotation_{}.mat".format(annotation_path, image_id)
            bb = file_io.FileMat().read(annotation_file)["box_coord"][0]
            roi = utils.crop_bb(image, bb, padding=padding, dst_size=self._patch_size)
            
            patches = (roi, cv2.flip(roi, 1)) if augment else (roi,)
            
            # Todo : augment modulization
            features = self._desc.describe(patches)
            features_set += features.tolist()
            
        labels = np.zeros((len(features_set), 1)) + label
        dataset = np.concatenate([labels, np.array(features_set)], axis=1)
        self._dataset += dataset.tolist()


    def add_negative_sets(self, image_dir, pattern, n_samples_per_img, sample_ratio=1.0):
        
        features_set = []
        image_files = self._get_image_files(image_dir, pattern, sample_ratio)

        for image_file in image_files:
            image = cv2.imread(image_file)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
             
            patches = utils.crop_random(image, self._patch_size, n_samples_per_img)
             
            features = self._desc.describe(patches)
            features_set += features.tolist()

        labels = np.zeros((len(features_set), 1))
        dataset = np.concatenate([labels, np.array(features_set)], axis=1)
        self._dataset += dataset.tolist()
    
    def save(self, data_file):
        file_io.FileHDF5().write(np.array(self._dataset), data_file, "label_and_features")

    def summary(self):
        
        labels = np.array(self._dataset)[:, 0]
        feature_shape = np.array(self._dataset)[:, 1:].shape
        
        n_positive_samples = len(labels[labels > 0])
        n_negative_samples = len(labels[labels == 0])
                                 
        print "[FeatureGetter INFO] Positive samples: {}, Negative samples: {}".format(n_positive_samples, n_negative_samples)
        print "[FeatureGetter INFO] Feature Dimension: {}".format(feature_shape[1])

    # Todo: configuration file 로 생성하는 구조로 바꾸자.
    @classmethod
    def load(cls, descriptor, patch_size, data_file=None):
        if data_file is None:
            dataset = []
        else:
            dataset = file_io.FileHDF5().read(data_file, "label_and_features")

        loaded = cls(descriptor, patch_size, dataset=dataset.tolist())
        return loaded

    @property
    def dataset(self):
        if self._dataset is None:
            raise ValueError('There is no dataset in this instance')
        else:
            return self._dataset
    
    def _get_image_files(self, directory, pattern, sample_ratio):
        image_files = file_io.list_files(directory, pattern)
        image_files = random.sample(image_files, int(len(image_files) * sample_ratio))
        return image_files

# Todo : FeatureExtractor class member function
def calc_average_patch_size(annotation_directory, pattern):
    widths = []
    heights = []
    
    files = file_io.list_files(annotation_directory, pattern)
    for file_ in files:  
        (y, h, x, w) = file_io.FileMat().read(file_)["box_coord"][0]
        widths.append(w - x)
        heights.append(h - y)

    height = np.mean(heights)
    width = np.mean(widths)
    return height, width




