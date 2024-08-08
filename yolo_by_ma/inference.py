from argparse import ArgumentParser
import os
import sys
import glob
import re

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), './pytorch_yolov3'))
import detect_image

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../common'))
from cdd import convert_darknettxt_dataset

global opts
opts = {}

def parseOptions():
    argparser = ArgumentParser()
    argparser.add_argument('--imgdir', help=':specify image file') # use action='store_true' as flag
    argparser.add_argument('--gentxt', help=':mode to gen bbox txt', action='store_true') # use action='store_true' as flag
    args = argparser.parse_args()
    if args.imgdir: opts.update({'imgdir':args.imgdir})
    if args.gentxt: opts.update({'gentxt':args.gentxt})

def main(imgdir, gentxt):
    args_config = "./yolov3_custom.yaml"
    args_weights = "./train_output/yolov3_final.pth"
    args_gpu_id = 0
    args_output = "./output"
    detector = detect_image.Detector(args_config, args_weights, args_gpu_id)

    label_file = "./custom_classes.txt"
    labels = convert_darknettxt_dataset.csvread(label_file)
    # print (f"%s %s" % (labels[0], labels[1]))

    # img_files = list(glob.glob(f"{imgdir}/*/*/*.jpg"))
    img_files = list(glob.glob(f'{imgdir}/*.jpg'))
    for image in img_files:
        detections, img_paths = detector.detect_from_path(image)
        for detection, img_path in zip(detections, img_paths):
            boxinfos = []
            check = [False, False]
            for box in detection:
                labelnum = None
                if box['class_name'] == labels[0][0]:
                    labelnum = 0
                if box['class_name'] == labels[1][0]:
                    labelnum = 1
                check[labelnum] = True

                if (gentxt):
                    darknetbb = convert_darknettxt_dataset.gen_darknetbb([box['x1'], box['y1'], box['x2'], box['y2']], img_path)
                    boxinfo = f"{labelnum} {darknetbb[0]} {darknetbb[1]} {darknetbb[2]} {darknetbb[3]}"
                    boxinfos.append(boxinfo)
                else:
                    boxinfo = f"{box['class_name']} {box['x1']:.0f} {box['y1']:.0f} {box['x2']:.0f} {box['y2']:.0f}"

                print(f"{box['confidence']:.0%}: {boxinfo}")
            if (check[0] == True and check[1] == True):
                if (gentxt):
                    txt_path = re.sub('\.jpg$', '.txt', img_path)
                    print (f"label0 and label1 are available in {img_path}, so {txt_path} is generated ...")
                    ofs = open(txt_path, mode='w')
                    for boxinfo in boxinfos:
                        ofs.write(f"{boxinfo}\n")
                    ofs.close()
                else:
                    print (f"label0 and label1 are available in {img_path}")
                # if not os.path.isdir(args_output):
                #     os.makedirs(args_output)
                # img = detect_image.Image.open(img_path)
                # detector.draw_boxes(img, detection)
                # img.save(args_output + "/" + detect_image.Path(img_path).name)
            else:
                print (f"label0 or label1 is not available in {img_path}")
                os.remove(img_path)

if __name__ == "__main__":
    parseOptions()
    if (opts.get('imgdir')):
        main(opts['imgdir'], opts.get('gentxt'))
