"""
常见的功能码
"""
from .libs.modbus_tk import defines as cst

# 功能码字典
funcs_dict = {
    1: {
        "name": "READ_COILS",
        "value": cst.READ_COILS,
        "info": "读线圈状态",
        "rw": 3,  # 读+写
        "detail": "由于历史原因，这个功能码表示线圈状态。其实不仅仅是线圈的状态，其它的数字输出状态也可以通过这个功能码读取，例如报警位，故障，异常。再比从设备为一个红外检测装置当感应到有人经过，红外会置低(0),那这个0状态就可以用此功能码读取。"
    },

    2: {
        "name": "READ_DISCRETE_INPUTS",
        "value": cst.READ_DISCRETE_INPUTS,
        "info": "读离散输入状态",
        "rw": 1,  # 读
        "detail": "读取外部开关量输入状态，例如面板上开关状态，光耦输入。由外部输入的变量一般主设备是无法修改，不过从设备是可以修改的。",
    },

    3: {
        "name": "READ_HOLDING_REGISTERS",
        "value": cst.READ_HOLDING_REGISTERS,
        "info": "读保持寄存器",
        "rw": 3,  # 读+写
        "detail": "内部输出量的寄存器，如配置参数。",
    },

    4: {
        "name": "READ_INPUT_REGISTERS",
        "value": cst.READ_INPUT_REGISTERS,
        "info": "读输入寄存器",
        "rw": 1,  # 读
        "detail": "读外部输入量的寄存器，这个输入可以是传感器的数据，可以是ad采集的电压电流数据等。",
    },

    5: {
        "name": "WRITE_SINGLE_COIL",
        "value": cst.WRITE_SINGLE_COIL,
        "info": "写单个线圈",
        "rw": 3,  # 读+写
        "detail": "写内部开关量状态，如继电器状态，IO状态。",
    },

    6: {
        "name": "WRITE_SINGLE_REGISTER",
        "value": cst.WRITE_SINGLE_REGISTER,
        "info": "写单个保持寄存器",
        "rw": 3,  # 读+写
        "detail": "写内部寄存器的值，如配置参数。",
    },

    15: {
        "name": "WRITE_MULTIPLE_COILS",
        "value": cst.WRITE_MULTIPLE_COILS,
        "info": "写多个线圈",
        "rw": 3,  # 读+写
        "detail": "写内部多个开关信号。",
    },

    16: {
        "name": "WRITE_MULTIPLE_REGISTERS",
        "value": cst.WRITE_MULTIPLE_REGISTERS,
        "info": "写多个保持寄存器",
        "rw": 3,  # 读+写
        "detail": "写内部多个寄存器的值，如配置参数较多，需分批传送。",
    },
}
