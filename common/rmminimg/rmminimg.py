#!/usr/bin/env python3

from argparse import ArgumentParser
import os
import sys
import glob
import re
import shutil
import cv2
import tensorflow as tf

class RemoveMinImage:
    def __init__(self):
        self.img_dir = None
        self.min_width = 526
        self.min_height = 791

    def parse_options(self):
        parser = ArgumentParser(description="Remove minimum size image processor")
        parser.add_argument('--img', type=str, help='specify image directory')

        args = parser.parse_args()
        self.img_dir = args.img

    def main(self):
        if not self.img_dir:
            print("Error: --img option must be specified.")
            return
        
        self.rm_min_img(self.img_dir)
        self.drop_empty_folders(self.img_dir)

    # === メインでコールされる関数群 ===
    def rm_min_img(self, imgdir, min_width=None, min_height=None):
        if min_width is None:
            min_width = self.min_width
        if min_height is None:
            min_height = self.min_height
            
        img_files = list(glob.glob(f'{imgdir}/*/*/*.jpg'))
        img_files.sort()

        for tgt in img_files:
            if os.path.isfile(tgt):
                if not self.is_valid_image(tgt):
                    print(f"Error: {tgt} can not opened!")
                    os.remove(tgt)
                else:
                    width, height, channels = self.get_resolution(tgt)
                    if width < min_width or height < min_height:
                        print(f"{tgt} = {width} x {height}, so removed.")
                        os.remove(tgt)
            elif os.path.isdir(tgt):
                if self.is_empty(tgt):
                    print(f"{tgt} is empty, so removed.")
                    os.rmdir(tgt)

    def cp_img(self, imgdir):
        img_files = list(glob.glob(f'{imgdir}/*/*/*.jpg'))
        img_files.sort()

        samples = []
        dupchk = {}
        for src in img_files:
            m = re.findall(f'{imgdir}\/(.*)\/(.*)\/.*.jpg$', src)
            if m and m[0]:
                idx = 0
                dst = f'{imgdir}/%s_%s_%08d.jpg' % (m[0][0], m[0][1], idx)
                while os.path.isfile(dst) or dst in dupchk.keys():
                    idx = idx + 1
                    dst = f'{imgdir}/%s_%s_%08d.jpg' % (m[0][0], m[0][1], idx)
                samples.append({"src": src, "dst": dst})
                dupchk[dst] = True
        
        for sample in samples:
            print('%s -> %s' % (sample['src'], sample['dst']))
            shutil.move(sample['src'], sample['dst'])

    def drop_empty_folders(self, directory):
        img_files = glob.glob(f"{directory}/*/*/*")
        for tgt in img_files:
            if os.path.isfile(tgt):
                os.remove(tgt)
        
        for dirpath, dirnames, filenames in os.walk(directory, topdown=False):
            if not dirnames and not filenames:
                os.rmdir(dirpath)

    # === サブ関数群 ===
    def get_resolution(self, filepath):
        img = cv2.imread(filepath)
     
        if img is None:
            print("Failed to load image file.")
            sys.exit(1)
     
        if len(img.shape) == 3:
            height, width, channels = img.shape[:3]
        else:
            height, width = img.shape[:2]
            channels = 1
        
        return width, height, channels

    def is_empty(self, directory):
        files = os.listdir(directory)
        files = [f for f in files if not f.startswith(".")]
        return not files

    def is_valid_image(self, filepath):
        try:
            with open(filepath, "rb") as fobj:
                is_jfif = tf.compat.as_bytes("JFIF") in fobj.peek(10)
            return is_jfif
        except Exception:
            return False

if __name__ == '__main__':
    processor = RemoveMinImage()
    processor.parse_options()
    processor.main()
