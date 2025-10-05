#!/usr/bin/env python3

from argparse import ArgumentParser
import os
import sys

import inference

sys.path.append(os.path.abspath('../common'))
from cdd import convert_darknettxt_dataset
from rmminimg import rmminimg
from df import df

class PrepareWebImages:
    def __init__(self):
        self.inference = inference.InferenceProcessor()

        self.cdd = convert_darknettxt_dataset.ConvertDarknetDataset()
        self.rmminimg = rmminimg.RemoveMinImage()
        self.df = df.DuplicateFinder()

        self.dwn = None
        self.lim = 10
        self.conv = None
        self.gentxt = None
        self.genimg = None

        self.imgsubdir = 'images'

    def parse_options(self):
        parser = ArgumentParser(description="Web images preparation processor")
        parser.add_argument('--dwn', help='generate download script', action='store_true')
        parser.add_argument('--lim', type=int, help='specify number of image on each name')
        parser.add_argument('--conv', help='convert image files', action='store_true')
        parser.add_argument('--gentxt', help='mode to gen txt for bbox', action='store_true')
        parser.add_argument('--genimg', help='mode to gen image with bbox', action='store_true')

        args = parser.parse_args()
        self.dwn = args.dwn
        if args.lim:
            self.lim = args.lim
        self.conv = args.conv
        self.gentxt = args.gentxt
        self.genimg = args.genimg

    def main(self):
        if self.dwn:
            self.generate_download_script()
        
        if self.conv:
            self.convert_images()

    # === メインでコールされる関数群 ===
    def generate_download_script(self):
        names = self.load_names()
        names = list(dict.fromkeys(names))
        names.sort()

        keyword_ary = self.load_keywords()
        exe = '../../common/gid/gid.py'

        dst_dir = f'./{self.imgsubdir}'
        if not os.path.isdir(dst_dir):
            os.makedirs(dst_dir)
        
        self.write_download_script(dst_dir, exe, names, keyword_ary)

    def convert_images(self):
        self.rmminimg.rm_min_img(self.imgsubdir)
        self.rmminimg.cp_img(self.imgsubdir)
        self.rmminimg.drop_empty_folders(self.imgsubdir)
        self.rmminimg.drop_empty_folders(self.imgsubdir)
        
        self.inference.main(self.imgsubdir, self.gentxt, self.genimg)

        self.df.img(self.imgsubdir)
        self.df.prt()
        self.df.mvp()
        self.df.clr()

    # === サブ関数群 ===
    def load_names(self):
        if os.path.isfile('names.txt'):
            raw_names = self.cdd.csvread('names.txt')
            return [' '.join(row) for row in raw_names]
        else:
            return ['cat', 'dog']

    def load_keywords(self):
        if os.path.isfile('kwd.txt'):
            raw_names = self.cdd.csvread('kwd.txt')
            return [' '.join(row) for row in raw_names]
        else:
            return ['black', 'small']

    def write_download_script(self, dst_dir, exe, names, keyword_ary):
        downcsh = f'{dst_dir}/down.sh'
        with open(downcsh, mode='w') as ofs:
            ofs.write(f"#!/usr/bin/env bash\n")
            kind = ' '.join(keyword_ary)
            ofs.write(f"kind='{kind}'\n")
            ofs.write(f"limit='{self.lim}'\n")
            for name in names:
                tgt = f"{name}"
                ofs.write(f"{exe} --tgt '{tgt}' --knd \"${{kind}}\" --lim \"${{limit}}\"\n")

if __name__ == '__main__':
    processor = PrepareWebImages()
    processor.parse_options()
    processor.main()
