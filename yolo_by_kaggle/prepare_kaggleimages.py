#!/usr/bin/env python3

from argparse import ArgumentParser
import os
import sys
import shutil
import re
import zipfile
from pathlib import Path

class Processor:
    def __init__(self):
        self.dwn = False
        self.zip = False
        self.dataset = 'kagglecatsanddogs_5340.zip'
        self.org_dir = './PetImages'
        self.dst_dir = './images'

    # オプション抽出
    def parse_options(self):
        parser = ArgumentParser(description="Dataset download and processing tool")
        parser.add_argument('--dwn', help='Download dataset', action='store_true')
        parser.add_argument('--zip', help='Extract zip file and move to images', action='store_true')
        
        args = parser.parse_args()
        self.dwn = args.dwn
        self.zip = args.zip

    # メイン
    def main(self):
        if self.dwn:
            self.download_dataset()
        
        if self.zip:
            self.process_zip()

    # メインでコールされる関数
    def download_dataset(self):
        url = f"https://download.microsoft.com/download/3/E/1/3E1C3F21-ECDB-4869-8368-6DEBA77B919F/{self.dataset}"
        os.system(f"curl -LO {url}")

    def process_zip(self):
        self.cleanup_directories()
        self.extract_zip()
        self.remove_unnecessary_files()
        self.organize_images()
        self.cleanup_source_directory()

    # サブ関数
    def cleanup_directories(self):
        if os.path.isdir(self.org_dir):
            shutil.rmtree(self.org_dir)
        if os.path.isdir(self.dst_dir):
            shutil.rmtree(self.dst_dir)

    def extract_zip(self):
        with zipfile.ZipFile(f"./{self.dataset}") as existing_zip:
            existing_zip.extractall('./')

    def remove_unnecessary_files(self):
        os.remove('./CDLA-Permissive-2.0.pdf')
        os.remove('./readme[1].txt')
        os.makedirs(self.dst_dir)

    def organize_images(self):
        p = Path(self.org_dir)
        image_ary = list(p.glob("**/*.jpg"))
        for image in image_ary:
            m = re.findall('PetImages\/(\w+)\/(\d+)\.jpg', str(image))
            if m and m[0]:
                cat = m[0][0]
                num = int(m[0][1])
                dst_file = '%s/%s%08d.jpg' % (self.dst_dir, cat, num)
                print('mv %s to %s' % (image, dst_file))
                shutil.move(image, dst_file)

    def cleanup_source_directory(self):
        if os.path.isdir(self.org_dir):
            shutil.rmtree(self.org_dir)

if __name__ == '__main__':
    processor = Processor()
    processor.parse_options()
    processor.main()
