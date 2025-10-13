yolo_by_cds — End-to-End Object Detection (YOLOv3, PyTorch)

yolo_by_cds is a compact, reproducible pipeline for object detection using the YOLO family (YOLOv3, PyTorch).
It supports two practical workflows:

yolo_by_kaggle/ — Train on a Kaggle dataset that already includes YOLO-format annotations (.txt).

yolo_by_web/ — Use weights you trained to auto-annotate new images (pseudo-labeling) and iterate.

Annotation is done with Yolo_Label, and both training and inference rely on a PyTorch YOLOv3 implementation.
Each subproject provides a run.sh to execute the entire flow end-to-end.

Repository Layout
yolo_by_cds/
├─ yolo_by_kaggle/        # Train/evaluate using an annotated Kaggle dataset
│  └─ run.sh              # One-shot script: setup → download → train → evaluate → export
│
├─ yolo_by_web/           # Auto-annotation (pseudo-labeling) using trained weights
│  └─ run.sh              # One-shot script: setup → infer → generate labels → (optionally) retrain
│
└─ README.md              # You are here

Key Components

Annotation: [Yolo_Label] — Create/edit bounding boxes and export in YOLO txt format.

Training/Inference: A PyTorch YOLOv3 codebase (cloned/used inside the scripts).

Auto-annotation (Pseudo-labels): yolo_by_web runs inference with your trained weights and emits YOLO-format labels you can review and use for retraining.

What is YOLO txt format?
For each image image.jpg, there is a image.txt with one line per object:
class_id x_center y_center width height (all normalized to 0–1).
