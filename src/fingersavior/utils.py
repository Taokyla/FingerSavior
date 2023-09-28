import time
from pathlib import Path
from random import randint

import cv2
import numpy


def random_int(min_num: int, max_num: int):
    if max_num < min_num:
        min_num, max_num = max_num, min_num
    rand = numpy.random.randn()
    num = int((max_num - min_num) / 2.0 * (rand / 2.5) + (min_num + max_num) / 2.0)
    if num < min_num or num > max_num:
        return random_int(min_num, max_num)
    return num


def get_now(time_format: str = "%Y-%m-%d %H%M%S"):
    return time.strftime(time_format, time.localtime())

def load_image(file_path: str | Path):
    if not isinstance(file_path, Path):
        file_path = Path(file_path)
    if file_path.exists() and file_path.is_file():
        cv_img = cv2.imdecode(numpy.fromfile(file_path, dtype=numpy.uint8), -1)
        return cv_img

def random_sleep(min_time: int = 800, max_time: int = 1600):
    if min_time > max_time:
        min_time, max_time = max_time, min_time
    time.sleep(randint(min_time, max_time) / 1000.0)
