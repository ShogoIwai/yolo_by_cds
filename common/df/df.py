#!/usr/bin/env python3

from argparse import ArgumentParser
import os

class DuplicateFinder:
    def __init__(self):
        self.img_dir = None
        self.prt_flag = None
        self.mvp_flag = None
        self.shw_flag = None
        self.clr_flag = None
        
        fp = os.path.dirname(os.path.abspath(__file__))
        self.dfp = f"python {fp}/duplicate_finder.py"
        self.db = f"~/.dfdb"

    def parse_options(self):
        parser = ArgumentParser(description="Duplicate image finder processor")
        parser.add_argument('--img', type=str, help='specify picture directory to database')
        parser.add_argument('--prt', help='only print duplicate pictures', action='store_true')
        parser.add_argument('--mvp', help='move all found duplicate pictures to the trash', action='store_true')
        parser.add_argument('--shw', help='show database', action='store_true')
        parser.add_argument('--clr', help='clear database', action='store_true')

        args = parser.parse_args()
        self.img_dir = args.img
        self.prt_flag = args.prt
        self.mvp_flag = args.mvp
        self.shw_flag = args.shw
        self.clr_flag = args.clr

    def main(self):
        if self.img_dir:
            self.img(self.img_dir)
        if self.prt_flag:
            self.prt()
        if self.mvp_flag:
            self.mvp()
        if self.shw_flag:
            self.shw()
        if self.clr_flag:
            self.clr()

    # === メインでコールされる関数群 ===
    def img(self, dir_path):
        os.system(f"{self.dfp} add {dir_path} --db {self.db}")

    def prt(self):
        os.system(f"{self.dfp} find --print --db {self.db}")

    def mvp(self):
        os.system(f"{self.dfp} find --delete --db {self.db}")

    def shw(self):
        os.system(f"{self.dfp} show --db {self.db}")

    def clr(self):
        os.system(f"{self.dfp} clear --db {self.db}")

if __name__ == '__main__':
    processor = DuplicateFinder()
    processor.parse_options()
    processor.main()
