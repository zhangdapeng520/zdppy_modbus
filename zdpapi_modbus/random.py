"""
生成随机数
"""
import random


def rand_float(min: int, max: int) -> float:
    """
    生成随机的浮点数
    """
    return random.random() * (max - min + 1) + min
