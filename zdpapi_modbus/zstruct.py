# -*- coding:utf-8 -*-
import struct
from typing import List, Tuple
import random

# modbus的类型字典
TYPE_DICT = {
    "c": {
        "C": "char",  # c语言中的类型
        "python": "string of length 1",  # python中的类型
        "byte": 1,  # 字节个数，也是modbus中的长度
    },
    "b": {
        "C": "singed char",
        "python": "integer",
        "byte": 1,
        "address": 1
    },
    "B": {
        "C": "unsigned char",
        "python": "integer",
        "byte": 1,
        "address": 1
    },
    "?": {
        "C": "_Bool",
        "python": "bool",
        "byte": 1,
        "address": 1
    },
    "h": {
        "C": "short",
        "python": "integer",
        "byte": 2,
        "address": 1
    },

    "H": {
        "C": "unsigned short",
        "python": "integer",
        "byte": 2,
        "address": 1
    },
    "i": {
        "C": "int",
        "python": "integer",
        "byte": 4,
        "address": 2
    },
    "I": {
        "C": "unsigned int",
        "python": "integer",
        "byte": 4,
        "address": 2
    },
    "l": {
        "C": "long",
        "python": "integer",
        "byte": 4,
        "address": 2
    },
    "L": {
        "C": "unsigned long",
        "python": "long",
        "byte": 4,
        "address": 2
    },
    "q": {
        "C": "long long",
        "python": "long",
        "byte": 8,
        "address": 4  # address表示modbus寄存器位置，1个位置能表示2个字节
    },
    "Q": {
        "C": "unsigned long long",
        "python": "long",
        "byte": 8,
        "address": 4
    },
    "f": {
        "C": "float",
        "python": "float",
        "byte": 4,
        "address": 2
    },

    "d": {
        "C": "double",
        "python": "float",
        "byte": 8,
        "address": 4,
    },

    "s": {
        "C": "char[]",
        "python": "string",
    },
    "p": {
        "C": "char[]",
        "python": "float",
    },
    "P": {
        "C": "void *",
        "python": "long",
    },
}


def get_length(type_str):
    """
    获取数据类型的对应字节个数
    @ param type_str：类型字符串
    """
    """"""
    type_ = TYPE_DICT.get(type_str)
    # 查原本的
    if type_ is not None:
        return type_.get("byte")

    # 查小写的
    type_ = TYPE_DICT.get(type_str.lower())
    if type_ is not None:
        return type_.get("byte")
    raise Exception(f"不存在该数据类型：{type_str}")


def get_address_length(type_str):
    """
    获取指定数据类型占用多少个内存地址
    """
    type_ = TYPE_DICT.get(type_str)

    # 查原本的
    if type_ is not None:
        return type_.get("address")

    # 查小写的
    type_ = TYPE_DICT.get(type_str.lower())
    if type_ is not None:
        return type_.get("address")

    raise Exception(f"不存在该数据类型：{type_str}")


def get_data_real_length(type_str, data_length):
    """
    获取真实数据的个数

    @param type_str： 类型字符串
    @param data_length: 数据长度，字节个数
    """

    # modbus地址位个数
    address_length = get_address_length(type_str)

    # 数据长度 // 单个需要的地址位个数
    result = data_length // address_length

    return result


def trans_float_to_int(num_arr: List[float]) -> Tuple[int]:
    """
    将浮点型转换为整型

    @param num_arr：浮点数的列表
    """
    msg = struct.pack(f"{len(num_arr)}f", *num_arr)
    b = struct.unpack(f"{len(num_arr) * 2}H", msg)
    return b


def trans_int_to_float(num_arr: List[int], keep_num: int = 2) -> List[float]:
    """
    将整数类型转换为浮点数类型

    @param num_arr: 整数类型的数组
    @param keep_num: 保留多少位小数
    """
    if num_arr is None:
        return []
    
    r = struct.unpack(f"{len(num_arr) // 2}f",
                      struct.pack(f"{len(num_arr)}H", *num_arr))
    r = [round(i, keep_num) for i in r]
    return r


def transform_type_arr(type_str, num_arr, keep_num=2, reverse=False):
    """
    根据类型字符串转换数据类型
    """
    result = []
    if type_str.lower() == "f":  # 浮点数类型
        if reverse:
            # 将整数数组转换为浮点数数组
            result = trans_int_to_float(num_arr, keep_num=keep_num)

        # 将浮点数数组转换为整数数组
        else:
            result = trans_float_to_int(num_arr)

    elif type_str.lower() == "b":  # 布尔值类型
        # 不需要解析和反解析
        result = num_arr

    return result


def pack_byte(data: List[int]):
    """
    打包短整数
    """
    return struct.pack(f"{len(data)}h", *data)


def pack_int(data: List[int]):
    """
    打包整数
    """
    return struct.pack(f"{len(data)}i", *data)


def pack_long(data: List[int]):
    """
    打包长整数
    """
    return struct.pack(f"{len(data)}l", *data)


def pack_float(data: List[float]):
    """
    打包单精度浮点数
    """
    return struct.pack(f"{len(data)}f", *data)


def pack_double(data: List[float]):
    """
    打包双精度浮点数
    """
    return struct.pack(f"{len(data)}d", *data)


def unpack_byte(data_length: int, msg) -> List[int]:
    """
    解包短短整数
    :param data_length: 原始数据长度，原始数据元素个数
    :param msg: 打包的消息字符串
    :return: 解包结果的元素列表
    """
    origin_format = f"{data_length}h"
    format = f"{data_length}h"

    b = struct.unpack(format, msg)
    r = struct.unpack(origin_format, struct.pack(format, *b))
    r = list(r)
    return r


def unpack_int(data_length: int, msg) -> List[int]:
    """
    解包整数
    :param data_length: 原始数据长度，原始数据元素个数
    :param msg: 打包的消息字符串
    :return: 解包结果的元素列表
    """
    origin_format = f"{data_length}i"
    format = f"{data_length}i"

    b = struct.unpack(format, msg)
    r = struct.unpack(origin_format, struct.pack(format, *b))
    r = list(r)
    return r


def unpack_long(data_length: int, msg) -> List[int]:
    """
    解包短长整数
    :param data_length: 原始数据长度，原始数据元素个数
    :param msg: 打包的消息字符串
    :return: 解包结果的元素列表
    """
    origin_format = f"{data_length}l"
    format = f"{data_length}l"

    b = struct.unpack(format, msg)
    r = struct.unpack(origin_format, struct.pack(format, *b))
    r = list(r)
    return r


def unpack_float(data_length: int, msg, float_keep_num: int = 2) -> List[float]:
    """
    解包单精度浮点型
    :param data_length: 原始数据长度，原始数据元素个数
    :param msg: 打包的消息字符串
    :return: 解包结果的元素列表
    """
    origin_format = f"{data_length}f"
    format = f"{data_length * 2}h"

    b = struct.unpack(format, msg)
    r = struct.unpack(origin_format, struct.pack(format, *b))
    r = list(map(lambda x: round(x, float_keep_num), r))
    return r


def unpack_double(data_length: int, msg, float_keep_num: int = 2) -> List[float]:
    """
    解包单精度浮点型
    :param data_length: 数据长度，原始数据有多少个数
    :param msg: 打包的消息字符串
    :param float_keep_num: 保留到小数点后的多少位
    :return: 解包结果的元素列表
    """
    origin_format = f"{data_length}d"
    format = f"{data_length * 4}h"
    b = struct.unpack(format, msg)
    r = struct.unpack(origin_format, struct.pack(format, *b))
    float_keep_num = len(str(int(float_keep_num))) + float_keep_num

    def float_to_int(x):  # 浮点数转换为指定小数位的浮点数
        r = len(str(int(x))) + float_keep_num
        return round(x, r)

    r = list(map(float_to_int, r))
    return r


def random_type_arr(type_str, min: int = 0, max: int = 100, length: int = 20, keep_num: int = 2):
    """
    根据类型生成数组
    """
    result = []
    if type_str.lower() == "f":  # 浮点数
        result = [
            round(random.random() * max + min, keep_num)
            for _ in range(length)
        ]
    elif type_str.lower() == "b":  # 布尔值
        result = [
            random.randint(0, 1)
            for _ in range(length)
        ]
    return result


if __name__ == '__main__':
    data = [11, 22, 33]
    # 测试打包
    print("============================================测试打包=====================================================")
    print(pack_byte(data))
    print(pack_int(data))
    print(pack_long(data))
    print(pack_float(data))
    print(pack_double(data))
    print("============================================测试完毕=====================================================\n\n")

    # 测试解包
    print("============================================测试解包=====================================================")
    print(unpack_byte(len(data), pack_byte(data)))
    print(unpack_int(len(data), pack_int(data)))
    print(unpack_long(len(data), pack_long(data)))
    print(unpack_float(len(data), pack_float(data)))
    print(unpack_double(len(data), pack_double(data)))
    print("============================================测试完毕=====================================================\n\n")
