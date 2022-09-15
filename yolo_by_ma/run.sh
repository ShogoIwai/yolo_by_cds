#!/usr/bin/env bash
#git clone https://github.com/nekobean/pytorch_yolov3

#python ./prepare_maimages.py --dwn
pushd images; bash ./down.sh; popd
python ./prepare_maimages.py --conv
rm -fr ./Trash

#mkdir -p ./txt; cp -f ./images/*.txt ./txt
#python ../common/cdd/convert_darknettxt_dataset.py ./ ./custom_classes.txt
#wget -nc https://pjreddie.com/media/files/darknet53.conv.74
#python ./pytorch_yolov3/train_custom.py --dataset_dir ./ --weights ./darknet53.conv.74 --config ./yolov3_custom.yaml
#python ./pytorch_yolov3/evaluate_custom.py --dataset_dir ./ --weight ./train_output/yolov3_final.pth --config ./yolov3_custom.yaml
