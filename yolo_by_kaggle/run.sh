#!/usr/bin/env bash

apply_patch() {
  local target="pytorch_yolov3/yolov3/utils/vis_utils.py"
  local patch_file="vis_utils.patch"
  
  echo "[patch] Checking patch status..."
  
  # ファイルの存在確認
  if [ ! -f "$target" ]; then
    echo "[ERROR] File not found: $target"
    echo "Please clone pytorch_yolov3 first:"
    echo "  git clone https://github.com/nekobean/pytorch_yolov3.git"
    return 1
  fi
  
  if [ ! -f "./$patch_file" ]; then
    echo "[ERROR] Patch file not found: ./$patch_file"
    return 1
  fi
  
  # 既にパッチが適用されているかチェック
  if grep -q 'draw\.textbbox' "$target"; then
    echo "[patch] already applied: $target"
    return 0
  fi
  
  echo "[patch] Applying patch to: $target"
  
  # pytorch_yolov3ディレクトリに移動してパッチ適用
  cd ./pytorch_yolov3 || return 1
  
  if patch -p1 < "../$patch_file"; then
    echo "[patch] Successfully applied!"
    cd - > /dev/null
    return 0
  else
    echo "[ERROR] Patch application failed"
    cd - > /dev/null
    return 1
  fi
}

git clone https://github.com/nekobean/pytorch_yolov3
apply_patch
if [ $? -ne 0 ]; then
  echo "[ERROR] Failed to apply patch. Exiting..."
  exit 1
fi
curl -L -o darknet53.conv.74 https://sourceforge.net/projects/yolov3.mirror/files/v8/darknet53.conv.74/
./prepare_kaggleimages.py --dwn
./prepare_kaggleimages.py --zip

../common/cdd/convert_darknettxt_dataset.py --input ./ --label ./custom_classes.txt

python ./pytorch_yolov3/train_custom.py --dataset_dir ./ --weights ./darknet53.conv.74 --config ./yolov3_custom.yaml

python ./pytorch_yolov3/evaluate_custom.py --dataset_dir ./ --weight ./train_output/yolov3_final.pth --config ./yolov3_custom.yaml
for image in ./images/Cat0001000*.jpg ./images/Dog0001000*.jpg; do
python inference.py --input $image --output ./output --weights ./train_output/yolov3_final.pth --config ./yolov3_custom.yaml
done
