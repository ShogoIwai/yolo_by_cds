#!/usr/bin/env bash
#git clone https://github.com/nekobean/pytorch_yolov3

#./prepare_kaggleimages.py --dwn
#./prepare_kaggleimages.py --zip
#../common/cdd/convert_darknettxt_dataset.py --input ./ --label ./custom_classes.txt

#curl -L -o darknet53.conv.74 https://sourceforge.net/projects/yolov3.mirror/files/v8/darknet53.conv.74/
python ./pytorch_yolov3/train_custom.py --dataset_dir ./ --weights ./darknet53.conv.74 --config ./yolov3_custom.yaml
#python ./pytorch_yolov3/evaluate_custom.py --dataset_dir ./ --weight ./train_output/yolov3_final.pth --config ./yolov3_custom.yaml

#for image in ./images/Cat0001000*.jpg ./images/Dog0001000*.jpg; do
#python inference.py --input $image --output ./output --weights ./train_output/yolov3_final.pth --config ./yolov3_custom.yaml
#done
