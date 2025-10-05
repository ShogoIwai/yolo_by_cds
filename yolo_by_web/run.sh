#!/usr/bin/env bash
git clone https://github.com/nekobean/pytorch_yolov3
curl -L -o darknet53.conv.74 https://sourceforge.net/projects/yolov3.mirror/files/v8/darknet53.conv.74/
./prepare_webimages.py --dwn --lim 50
pushd images; bash ./down.sh; popd

mkdir -p ./train_output; cp ../yolo_by_kaggle/train_output/yolov3_final.pth ./train_output/
./prepare_webimages.py --conv --gentxt --genimg
rm -fr ./Trash
mkdir -p ./txt; cp -f ./images/*.txt ./txt
../common/cdd/convert_darknettxt_dataset.py --input ./ --label ./custom_classes.txt

python ./pytorch_yolov3/train_custom.py --dataset_dir ./ --weights ./darknet53.conv.74 --config ./yolov3_custom.yaml

python ./pytorch_yolov3/evaluate_custom.py --dataset_dir ./ --weight ./train_output/yolov3_final.pth --config ./yolov3_custom.yaml
