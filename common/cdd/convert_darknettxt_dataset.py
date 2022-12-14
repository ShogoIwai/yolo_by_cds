import os
import sys

import argparse
from pathlib import Path
import re
import shutil
from PIL import Image
import csv
from sklearn.model_selection import train_test_split

global labels
labels = []
imgsubdir = 'images'
txtsubdir = 'txt'
lblsubdir = 'labels'

def parse_args():
    """Parse command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="path to source directory, image and txt dir are available")
    parser.add_argument("label", type=Path, help="path to label file")
    parser.add_argument(
        "--test_size",
        type=float,
        default=0.1,
        help="the proportion of the dataset to include in the test split",
    )
    args = parser.parse_args()

    return args

def csvread(file_name):
    with open(file_name, 'r') as csvfile:
        list_ary = []
        reader = csv.reader(csvfile, delimiter=' ')
        for row in reader:
            list_ary.append(row)

    return list_ary

def convert_label_idx2label(label_idx):
    label = None
    for i in range(len(labels)):
        if label_idx[0] == str(i):
            label = labels[i][0]
            return label

    return label

def convert_label_label2idx(label):
    idx = None
    for i in range(len(labels)):
        if label == labels[i][0]:
            idx = i
            return idx

    return idx

def round0max(val, max):
    ret = val
    if (ret > max): ret = max
    elif (ret < 0): ret = 0
    return ret

def gen_darknetbb(bb_ary, img_file):
    try:
        img_size = Image.open(img_file).size
    except Image.UnidentifiedImageError as err:
        # print("UnidentifiedImageError: %s" % (err))
        return None

    img_width = img_size[0]
    img_height = img_size[1]

    x_max_rect = round0max(int(bb_ary[2]), img_width-1)
    y_max_rect = round0max(int(bb_ary[3]), img_height-1)
    x_min_rect = round0max(int(bb_ary[0]), x_max_rect-1)
    y_min_rect = round0max(int(bb_ary[1]), y_max_rect-1)

    x_values = [float(x_min_rect/img_width), float(x_max_rect/img_width)]
    y_values = [float(y_min_rect/img_height), float(y_max_rect/img_height)]

    center_x = (x_values[0] + x_values[1]) / 2
    center_y = (y_values[0] + y_values[1]) / 2

    w = x_values[1] - x_values[0]
    h = y_values[1] - y_values[0]

    return [round0max(center_x, 1), round0max(center_y, 1), round0max(w, 1), round0max(h, 1)]

def extract_coor(bb_info, img_width, img_height):
    x_rect_mid  = float(bb_info[1])
    y_rect_mid  = float(bb_info[2])
    width_rect  = float(bb_info[3])
    height_rect = float(bb_info[4])

    x_min_rect = int(((2 * x_rect_mid * img_width)  - (width_rect * img_width)) / 2)
    y_min_rect = int(((2 * y_rect_mid * img_height) - (height_rect * img_height)) / 2)
    x_max_rect = int(((2 * x_rect_mid * img_width)  + (width_rect * img_width)) / 2)
    y_max_rect = int(((2 * y_rect_mid * img_height) + (height_rect * img_height)) / 2)

    return x_min_rect, y_min_rect, x_max_rect, y_max_rect

def conv_label(img_file, txt_file):
    try:
        bb_ary = csvread(txt_file)
    except FileNotFoundError as err:
        # print("FileNotFoundError: %s" % (err))
        return None

    try:
        img_size = Image.open(img_file).size
    except Image.UnidentifiedImageError as err:
        # print("UnidentifiedImageError: %s" % (err))
        return None

    try:
        img_depth = Image.open(img_file).layers
    except AttributeError as err:
        # print("AttributeError: %s" % (err))
        return None

    img_width = img_size[0]
    img_height = img_size[1]
    list_ary = []
    for i in range(len(bb_ary)):
        label = convert_label_idx2label(bb_ary[i][0])
        x_min_rect, y_min_rect, x_max_rect, y_max_rect = extract_coor(bb_ary[i], img_width, img_height)
        list_ary.append([label, x_min_rect, y_min_rect, x_max_rect, y_max_rect]) 

    txt_basename = os.path.basename(txt_file)
    txt_basename_rep = re.sub('\.', '\.', txt_basename)
    ptn = '%s\/%s$' % (txtsubdir, txt_basename_rep)
    result = '%s/%s' % (lblsubdir, txt_basename)
    txt_file = re.sub(ptn, result, str(txt_file))
    with open(txt_file, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=' ')
        writer.writerows(list_ary)

    return txt_file

def load_dataset(dataset_dir, label_file):
    img_files = list(dataset_dir.glob(f"{imgsubdir}/*.jpg"))
    global labels
    labels = csvread(label_file)

    label_dir = dataset_dir / lblsubdir
    if os.path.isdir(label_dir):
        shutil.rmtree(label_dir)
    os.makedirs(label_dir)

    samples = []
    for img_file in img_files:
        txt_file = os.path.basename(img_file)
        txt_file = re.sub('\.jpg$', '.txt', txt_file)
        txt_file = dataset_dir / f"{txtsubdir}" / txt_file
        txt_file = conv_label(img_file, txt_file)
        if txt_file is not None:
            samples.append({"image": img_file, "label": txt_file})

    return samples

def output_dataset(output_dir, samples, test_size):
    train_samples, test_samples = train_test_split(samples, test_size=test_size, random_state=42)

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
            f.write(f"{output_dir}/{imgsubdir}/{sample['image'].name}")
            with open(f"{output_dir}/{sample['label']}", 'r') as label:
                for bb in label:
                    bb = re.sub('\n', '', bb)
                    m = re.findall('(\w+)', bb)
                    if (len(m) == 5):
                        bb = m[1] + ',' + m[2] + ',' + m[3] + ',' + m[4] + ',' + str(convert_label_label2idx(m[0]))
                    f.write(" " + bb)
            f.write("\n")

    with open(output_dir / "test_annotation.txt", "w") as f:
        for sample in test_samples:
            f.write(f"{output_dir}/{imgsubdir}/{sample['image'].name}")
            with open(f"{output_dir}/{sample['label']}", 'r') as label:
                for bb in label:
                    bb = re.sub('\n', '', bb)
                    m = re.findall('(\w+)', bb)
                    if (len(m) == 5):
                        bb = m[1] + ',' + m[2] + ',' + m[3] + ',' + m[4] + ',' + str(convert_label_label2idx(m[0]))
                    f.write(" " + bb)
            f.write("\n")

def main():
    args = parse_args()

    samples = load_dataset(args.input, args.label)
    # print(samples)
    output_dataset(args.input, samples, args.test_size)

if __name__ == "__main__":
    main()
