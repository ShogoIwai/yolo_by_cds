#!/usr/bin/env python3

import os
import sys
import math
import re
import csv
import shutil
import random
from argparse import ArgumentParser
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple, TypeVar, Optional
from PIL import Image

T = TypeVar("T")

class Processor:
    def __init__(self):
        self.input_dir = None
        self.label_file = None
        self.test_size = 0.1
        self.labels = []
        self.imgsubdir = 'images'
        self.txtsubdir = 'txt'
        self.lblsubdir = 'labels'

    def parse_options(self):
        parser = ArgumentParser(description="YOLO dataset processor")
        parser.add_argument("--input", type=Path, help="path to source directory, image and txt dir are available")
        parser.add_argument("--label", type=Path, help="path to label file")
        parser.add_argument("--test_size",
            type=float,
            default=0.1,
            help="the proportion of the dataset to include in the test split",
        )

        args = parser.parse_args()
        self.input_dir = args.input
        self.label_file = args.label
        self.test_size = args.test_size

    def main(self):
        if not (self.input_dir and self.label_file):
            print("Error: input and label arguments must be specified.")
            return

        samples = self.load_dataset(self.input_dir, self.label_file)
        self.output_dataset(self.input_dir, samples, self.test_size)

    # === メインでコールされる関数群 ===
    def load_dataset(self, dataset_dir, label_file):
        img_files = list(dataset_dir.glob(f"{self.imgsubdir}/*.jpg"))
        self.labels = self.csvread(label_file)

        label_dir = dataset_dir / self.lblsubdir
        if os.path.isdir(label_dir):
            shutil.rmtree(label_dir)
        os.makedirs(label_dir)

        samples = []
        for img_file in img_files:
            txt_file = os.path.basename(img_file)
            txt_file = re.sub('\.jpg$', '.txt', txt_file)
            txt_file = dataset_dir / f"{self.txtsubdir}" / txt_file
            txt_file = self.conv_label(img_file, txt_file)
            if txt_file is not None:
                samples.append({"image": img_file, "label": txt_file})

        return samples

    def output_dataset(self, output_dir, samples, test_size):
        train_samples, test_samples = self.train_test_split_compat(samples, test_size=test_size, random_state=42)

        # for pytorch_yolov3
        with open(output_dir / "train.txt", "w") as f:
            for sample in train_samples:
                f.write(f"{sample['image'].name}\n")

        with open(output_dir / "test.txt", "w") as f:
            for sample in test_samples:
                f.write(f"{sample['image'].name}\n")

        # for YOLOv4-pytorch
        with open(output_dir / "train_annotation.txt", "w") as f:
            for sample in train_samples:
                f.write(f"{output_dir}/{self.imgsubdir}/{sample['image'].name}")
                with open(f"{output_dir}/{sample['label']}", 'r') as label:
                    for bb in label:
                        bb = re.sub('\n', '', bb)
                        m = re.findall('(\w+)', bb)
                        if (len(m) == 5):
                            bb = m[1] + ',' + m[2] + ',' + m[3] + ',' + m[4] + ',' + str(self.convert_label_label2idx(m[0]))
                        f.write(" " + bb)
                f.write("\n")

        with open(output_dir / "test_annotation.txt", "w") as f:
            for sample in test_samples:
                f.write(f"{output_dir}/{self.imgsubdir}/{sample['image'].name}")
                with open(f"{output_dir}/{sample['label']}", 'r') as label:
                    for bb in label:
                        bb = re.sub('\n', '', bb)
                        m = re.findall('(\w+)', bb)
                        if (len(m) == 5):
                            bb = m[1] + ',' + m[2] + ',' + m[3] + ',' + m[4] + ',' + str(self.convert_label_label2idx(m[0]))
                        f.write(" " + bb)
                f.write("\n")

    # === サブ関数群 ===
    def train_test_split_compat(
        self,
        samples: Sequence[T],
        test_size: int | float,
        random_state: Optional[int] = None,
        shuffle: bool = True,
    ) -> Tuple[List[T], List[T]]:
        """
        sklearn.model_selection.train_test_split の最小互換:
            - 単一配列 samples を train/test に分割して返す
            - test_size は float (0<ts<1) または int (1<=ts<=len(samples))
            - random_state により決定的シャッフル

        返値: (train_samples, test_samples)
        """
        if not isinstance(samples, Sequence):
            raise TypeError("samples はシーケンスである必要があります")

        n = len(samples)
        if n == 0:
            return [], []

        n_test = self._compute_n_test(n, test_size)

        # インデックスをシャッフルしてからスライス
        indices = list(range(n))
        if shuffle:
            rng = random.Random(random_state)
            rng.shuffle(indices)

        test_indices = set(indices[:n_test])
        test = [samples[i] for i in range(n) if i in test_indices]
        train = [samples[i] for i in range(n) if i not in test_indices]
        return train, test

    def _compute_n_test(self, n: int, test_size: int | float) -> int:
        if isinstance(test_size, int):
            if not (0 <= test_size <= n):
                raise ValueError(f"整数の test_size は 0～{n} の範囲で指定してください")
            n_test = test_size
        else:
            n_test = int(math.ceil(n * test_size))
        if n_test > n:
            n_test = n
        return n_test

    def conv_label(self, img_file, txt_file):
        try:
            bb_ary = self.csvread(txt_file)
        except FileNotFoundError as err:
            return None

        try:
            img_size = Image.open(img_file).size
        except Image.UnidentifiedImageError as err:
            return None

        try:
            img_depth = Image.open(img_file).layers
        except AttributeError as err:
            return None

        img_width = img_size[0]
        img_height = img_size[1]
        list_ary = []
        for i in range(len(bb_ary)):
            label = self.convert_label_idx2label(bb_ary[i][0])
            x_min_rect, y_min_rect, x_max_rect, y_max_rect = self.extract_coor(bb_ary[i], img_width, img_height)
            list_ary.append([label, x_min_rect, y_min_rect, x_max_rect, y_max_rect])

        txt_basename = os.path.basename(txt_file)
        txt_basename_rep = re.sub('\.', '\.', txt_basename)
        ptn = '%s\/%s$' % (self.txtsubdir, txt_basename_rep)
        result = '%s/%s' % (self.lblsubdir, txt_basename)
        txt_file = re.sub(ptn, result, str(txt_file))
        with open(txt_file, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=' ')
            writer.writerows(list_ary)

        return txt_file

    def csvread(self, file_name):
        with open(file_name, 'r') as csvfile:
            list_ary = []
            reader = csv.reader(csvfile, delimiter=' ')
            for row in reader:
                list_ary.append(row)
        return list_ary

    def convert_label_idx2label(self, label_idx):
        label = None
        for i in range(len(self.labels)):
            if label_idx == str(i):
                label = self.labels[i][0]
                return label
        return label

    def convert_label_label2idx(self, label):
        idx = None
        for i in range(len(self.labels)):
            if label == self.labels[i][0]:
                idx = i
                return idx
        return idx

    def extract_coor(self, bb_info, img_width, img_height):
        x_rect_mid = float(bb_info[1])
        y_rect_mid = float(bb_info[2])
        width_rect = float(bb_info[3])
        height_rect = float(bb_info[4])

        x_min_rect = int(((2 * x_rect_mid * img_width) - (width_rect * img_width)) / 2)
        y_min_rect = int(((2 * y_rect_mid * img_height) - (height_rect * img_height)) / 2)
        x_max_rect = int(((2 * x_rect_mid * img_width) + (width_rect * img_width)) / 2)
        y_max_rect = int(((2 * y_rect_mid * img_height) + (height_rect * img_height)) / 2)

        return x_min_rect, y_min_rect, x_max_rect, y_max_rect

    def round0max(self, val, max):
        ret = val
        if (ret > max):
            ret = max
        elif (ret < 0):
            ret = 0
        return ret

    def gen_darknetbb(self, bb_ary, img_file):
        try:
            img_size = Image.open(img_file).size
        except Image.UnidentifiedImageError as err:
            return None

        img_width = img_size[0]
        img_height = img_size[1]

        x_max_rect = self.round0max(int(bb_ary[2]), img_width - 1)
        y_max_rect = self.round0max(int(bb_ary[3]), img_height - 1)
        x_min_rect = self.round0max(int(bb_ary[0]), x_max_rect - 1)
        y_min_rect = self.round0max(int(bb_ary[1]), y_max_rect - 1)

        x_values = [float(x_min_rect / img_width), float(x_max_rect / img_width)]
        y_values = [float(y_min_rect / img_height), float(y_max_rect / img_height)]

        center_x = (x_values[0] + x_values[1]) / 2
        center_y = (y_values[0] + y_values[1]) / 2

        w = x_values[1] - x_values[0]
        h = y_values[1] - y_values[0]

        return [self.round0max(center_x, 1), self.round0max(center_y, 1), self.round0max(w, 1), self.round0max(h, 1)]

if __name__ == '__main__':
    processor = Processor()
    processor.parse_options()
    processor.main()
