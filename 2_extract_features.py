#-*- coding: utf-8 -*-

import object_detector.extractor as extractor
import object_detector.file_io as file_io
import object_detector.descriptor as descriptor
import object_detector.factory as factory

CONFIGURATION_FILE = "conf/new_format.json"
PATCH_SIZE = (32, 96)

if __name__ == "__main__":
    conf = file_io.FileJson().read(CONFIGURATION_FILE)
     
    # 1. Build FeatureExtrator instance
    getter = factory.Factory.create_extractor(conf["descriptor"]["algorithm"], conf["descriptor"]["parameters"], PATCH_SIZE)
      
    # 2. Get Feature sets
    getter.add_positive_sets(image_dir=conf["dataset"]["pos_data_dir"],
                             pattern=conf["dataset"]["pos_format"], 
                             annotation_path=conf["dataset"]['annotations_dir'],
                             padding=conf["extractor"]['padding'],
                             )
     
    # Todo : positive sample 숫자에 따라 negative sample 숫자를 자동으로 정할 수 있도록 설정
    getter.add_negative_sets(image_dir=conf["dataset"]["neg_data_dir"],
                             pattern=conf["dataset"]["neg_format"],
                             n_samples_per_img=conf["extractor"]["num_patches_per_negative_image"],
                             sample_ratio=conf["extractor"]["sampling_ratio_for_negative_images"])
      
    getter.summary()
      
    # 3. Save dataset
    getter.save(data_file=conf["extractor"]["output_file"])
    del getter
      
    # 4. Test Loading dataset
    getter = factory.Factory.create_extractor(conf["descriptor"]["algorithm"], conf["descriptor"]["parameters"], PATCH_SIZE, conf["extractor"]["output_file"])
    getter.summary()
 
 
     