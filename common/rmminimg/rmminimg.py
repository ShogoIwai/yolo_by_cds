from argparse import ArgumentParser
import os
import sys

import glob
import re
import shutil
import cv2
import tensorflow as tf

global opts
opts = {}

def parseOptions():
    argparser = ArgumentParser()
    argparser.add_argument('--img', help=':specify image dir') # use action='store_true' as flag
    args = argparser.parse_args()
    if args.img: opts.update({'img':args.img})

def get_resolution(filepath):
    img = cv2.imread(filepath)
 
    if img is None:
        print("Failed to load image file.")
        sys.exit(1)
 
    if len(img.shape) == 3:
        height, width, channels = img.shape[:3]
    else:
        height, width = img.shape[:2]
        channels = 1
    
    return width,height,channels

def is_empty(directory):
    files = os.listdir(directory)
    files = [f for f in files if not f.startswith(".")]
    if not files:
        return True
    else:
        return False

def rm_min_img(imgdir, min_width=526, min_height=791):
    # img_files = glob.glob(f"{imgdir}/**", recursive=True)
    img_files = list(glob.glob(f'{imgdir}/*/*/*.jpg'))
    img_files.sort()
    # print(img_files)

    for tgt in img_files:
        if (os.path.isfile(tgt)):
            try:
                fobj = open(tgt, "rb")
                is_jfif = tf.compat.as_bytes("JFIF") in fobj.peek(10)
            finally:
                fobj.close()

            if not is_jfif:
                print(f"Error: {tgt} can not opend!")
                # Delete corrupted image
                os.remove(tgt)
            else:
                width,height,channels = get_resolution(tgt)
                if (width < min_width or height < min_height):
                    print(f"{tgt} = {width} x {height}, so removed.")
                    os.remove(tgt)

        elif (os.path.isdir(tgt)):
            if (is_empty(tgt)):
                print(f"{tgt} is empty, so removed.")
                os.rmdir(tgt)

def cp_img(imgdir):
    img_files = list(glob.glob(f'{imgdir}/*/*/*.jpg'))
    img_files.sort()
    # print(img_files)

    samples = []
    dupchk = {}
    for src in img_files:
        m = re.findall(f'{imgdir}\/(.*)\/(.*)\/.*.jpg$', src)
        if m[0]:
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

def drop_empty_folders(directory):
    img_files = glob.glob(f"{directory}/*/*/*")
    for tgt in img_files:
        os.remove(tgt)
    for dirpath, dirnames, filenames in os.walk(directory, topdown=False):
        if not dirnames and not filenames:
            os.rmdir(dirpath)

if __name__ == '__main__':
    parseOptions()
    if (opts.get('img')):
        rm_min_img(opts['img'])
        drop_empty_folders(opts['img'])
