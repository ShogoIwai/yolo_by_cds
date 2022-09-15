#!/usr/bin/env bash
git clone https://github.com/argusswift/YOLOv4-pytorch

python ./prepare_kaggleimages.py --dwn
python ./prepare_kaggleimages.py --zip

python ../common/cdd/convert_darknettxt_dataset.py ./ ./custom_classes.txt
python ../common/replace/replace.py --file ./YOLOv4-pytorch/config/yolov4_config.py --pre "PROJECT_PATH, 'data'" --post "PROJECT_PATH, '../'"
python ../common/replace/replace.py --file ./YOLOv4-pytorch/config/yolov4_config.py --pre "\"TYPE\": \"CoordAttention-YOLOv4\"" --post "\"TYPE\": \"Mobilenet-YOLOv4\""
python ../common/replace/replace.py --file ./YOLOv4-pytorch/config/yolov4_config.py --pre "\"DATA_TYPE\": \"VOC\"" --post "\"DATA_TYPE\": \"Customer\""
python ../common/replace/replace.py --file ./YOLOv4-pytorch/config/yolov4_config.py --pre "\"NUM\": 3" --post "\"NUM\": 2"
python ../common/replace/replace.py --file ./YOLOv4-pytorch/config/yolov4_config.py --pre "\"CLASSES\": \[\"unknown\", \"person\", \"car\"\]" --post "\"CLASSES\": [\"cat\", \"dog\"]"

python ./training1.py --gpu_id 0
python ./inference1.py --weight_path ./ backup_epoch119.pt --gpu_id 0
