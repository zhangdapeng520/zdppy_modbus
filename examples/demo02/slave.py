"""
按照1秒钟传递100台机组的数据，1台机组25个变量
"""

from zdpapi_modbus import cst, modbus_tcp, rand_float, trans_float_to_int
import time

# 创建一个TCP服务
server = modbus_tcp.TcpServer()

# 启动server
server.start()

# 添加一个slave
slave_id = 1
slave_1 = server.add_slave(slave_id)

# 添加一个block
block_name = "0"
slave_1.add_block(block_name, cst.HOLDING_REGISTERS, 0, 3000)

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

# 生成随机数
data_float = [rand_float(0, 100) for _ in data]

# 不断的写入数据
while True:
    # 生成数据

    # 写入数据
    slave = server.get_slave(slave_id)  # slave
    address = 0

    values = trans_float_to_int(data_float)
    value_length = len(values)
    print("要传输的数据个数：", value_length)
    index = 0
    while True:
        slave.set_values(block_name, index, values[index:index + 100])
        
        # 最后一次传输
        value_length -= 100
        if value_length <= 100:
            slave.set_values(block_name, index, values[index:])
            break
        
        # 每次传100个数
        index += 100

    time.sleep(1)
