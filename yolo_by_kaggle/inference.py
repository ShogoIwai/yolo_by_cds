import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), './pytorch_yolov3'))

import detect_image

if __name__ == "__main__":
    detect_image.main()
