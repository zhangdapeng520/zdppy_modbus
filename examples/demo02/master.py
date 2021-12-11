"""
从服务端获取100台机组的数据，每台机组有25个变量
"""
from zdpapi_modbus import cst, modbus_tcp, trans_int_to_float
import time
import random

master = modbus_tcp.TcpMaster()
master.set_timeout(5.0)
slave_id = 1


# 单台风机的数据
variables = [
    "机舱X方向振动",
    "机舱Y方向振动",
    "限功率运行状态",
    "电网有功功率",
    "有功功率",
    "风轮转速",
    "环境温度",
    "瞬时风向",
    "瞬时风速",
    "工作模式",
    "测试写入主控变量1",
    "1#风向仪瞬时风向",
    "2#风向仪瞬时风向",
    "机舱外风向",
    "偏航方位角",
    "测试（高频数据）1",
    "测试（高频数据）2",
    "测试（高频数据）3",
    "测试（高频数据）4",
    "测试（高频数据）5",
    "测试（高频数据）6",
    "测试（高频数据）7",
    "测试（高频数据）8",
    "测试（高频数据）9",
    "测试（高频数据）10",
]

# 分两个slave传，一个传50台风机
# 生成数据
data = []
address = 0
for i in range(1, 51):
    for j in range(1, len(variables)+1):
        control = {}
        control["device_id"] = i
        control["cname"] = variables[j-1]
        control["name"] = f"v{i}_{j}"
        address += 2
        control["address"] = address
        control["length"] = 2
        control["func"] = 3
        control["type"] = "F"
        data.append(control)

while True:
    # 读取数据
    data = []
    data_length = 2500  # 要取出2500个数
    index = 0
    while True:
        # 每次取出100个数
        length = 100
        values = master.execute(
            slave_id, cst.READ_HOLDING_REGISTERS, index, length)
        data.extend(values)

        # 最后一次取
        data_length -= 100
        if data_length <= 100:
            values = master.execute(
                slave_id, cst.READ_HOLDING_REGISTERS, index, data_length)
            data.extend(values)
            break

        index += 100

    # print("data:", data, len(data))

    # 解析为真实的数组
    result = trans_int_to_float(data, keep_num=2)
    print("最终结果：", result, len(result))

    # 1s执行一次
    time.sleep(1)
