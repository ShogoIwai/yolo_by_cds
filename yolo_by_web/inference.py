#!/usr/bin/env python3

from argparse import ArgumentParser
import os
import sys
import glob
import re

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), './pytorch_yolov3'))
import detect_image

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../common'))
from cdd import convert_darknettxt_dataset

class InferenceProcessor:
    def __init__(self):
        self.cdd = convert_darknettxt_dataset.ConvertDarknetDataset()

        self.imgdir = None
        self.gentxt = None
        self.genimg = None

        self.args_config = "./yolov3_custom.yaml"
        self.args_weights = "./train_output/yolov3_final.pth"
        self.args_gpu_id = 0
        self.args_output = "./output"
        self.label_file = "./custom_classes.txt"
        self.labels = []
        self.detector = None

    def parse_options(self):
        parser = ArgumentParser(description="YOLO inference processor")
        parser.add_argument('--imgdir', type=str, help='specify image directory')
        parser.add_argument('--gentxt', help='mode to gen txt for bbox', action='store_true')
        parser.add_argument('--genimg', help='mode to gen image with bbox', action='store_true')

        args = parser.parse_args()
        self.imgdir = args.imgdir
        self.gentxt = args.gentxt
        self.genimg = args.genimg

    def main(self, imgdir=None, gentxt=None, genimg=None):
        # 引数が指定された場合は上書き(外部から呼ばれた場合用)
        if imgdir is not None:
            self.imgdir = imgdir
        if gentxt is not None:
            self.gentxt = gentxt
        if genimg is not None:
            self.genimg = genimg

        if not self.imgdir:
            print("Error: --imgdir option must be specified.")
            return

        self.initialize_detector()
        self.process_images()

    # === メインでコールされる関数群 ===
    def initialize_detector(self):
        self.detector = detect_image.Detector(
            self.args_config, 
            self.args_weights, 
            self.args_gpu_id
        )
        self.labels = self.cdd.csvread(self.label_file)

    def process_images(self):
        img_files = list(glob.glob(f'{self.imgdir}/*.jpg'))
        
        for image in img_files:
            detections, img_paths = self.detector.detect_from_path(image)
            for detection, img_path in zip(detections, img_paths):
                self.process_detection(detection, img_path)

    def process_detection(self, detection, img_path):
        boxinfos = []
        check = [False, False]
        
        for box in detection:
            labelnum = self.get_label_number(box['class_name'])
            if labelnum is not None:
                check[labelnum] = True
            
            boxinfo = self.generate_box_info(box, img_path, labelnum)
            if self.gentxt and boxinfo:
                boxinfos.append(boxinfo)
            
            if boxinfo:
                print(f"{box['confidence']:.0%}: {boxinfo}")
        
        self.handle_detection_result(detection, img_path, check, boxinfos)

    def handle_detection_result(self, detection, img_path, check, boxinfos):
        if check[0] == True or check[1] == True:
            print(f"label0 or label1 are available in {img_path}")
            if self.gentxt:
                self.generate_txt_file(img_path, boxinfos)
            if self.genimg:
                if not os.path.isdir(self.args_output):
                    os.makedirs(self.args_output)
                img = detect_image.Image.open(img_path)
                self.detector.draw_boxes(img, detection)
                img.save(self.args_output + "/" + detect_image.Path(img_path).name)
        else:
            print(f"label0 or label1 is not available in {img_path}")
            os.remove(img_path)

    # === サブ関数群 ===
    def get_label_number(self, class_name):
        for i, label in enumerate(self.labels):
            if class_name == label[0]:
                return i
        return None

    def generate_box_info(self, box, img_path, labelnum):
        if self.gentxt:
            darknetbb = self.cdd.gen_darknetbb(
                [box['x1'], box['y1'], box['x2'], box['y2']], 
                img_path
            )
            return f"{labelnum} {darknetbb[0]} {darknetbb[1]} {darknetbb[2]} {darknetbb[3]}"
        else:
            return f"{box['class_name']} {box['x1']:.0f} {box['y1']:.0f} {box['x2']:.0f} {box['y2']:.0f}"

    def generate_txt_file(self, img_path, boxinfos):
        txt_path = re.sub('\.jpg$', '.txt', img_path)
        print(f"label0 or label1 are available in {img_path}, so {txt_path} is generated ...")
        
        with open(txt_path, mode='w') as ofs:
            for boxinfo in boxinfos:
                ofs.write(f"{boxinfo}\n")

if __name__ == "__main__":
    processor = InferenceProcessor()
    processor.parse_options()
    processor.main()
