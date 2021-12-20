from zdpapi_modbus import Slave, rand_float
import sys
import asyncio
from config import controls

# 动态参数
port = int(sys.argv[1])  # 启动仿真的端口
device_num = int(sys.argv[2])  # 启动仿真设备数量

# 单台设备主控长度
device_values = list(controls.values())
print("设备主控值：", device_values)
device_length = sum(device_values)

# 实际长度
length = int(device_num * device_length)

# 最大长度
max_length = length * 3

print("设备数量：", device_num)
print("每个设备主控数量：", device_length)
print("block的最大长度：", max_length)

# 创建slave
slave = Slave("0.0.0.0", port)
slave.add_slave(1)
slave.add_block(1, "0", 3, 0, max_length)

async def run():
    slave.start()
    while True:
        data_float = [rand_float(0, 100) for _ in range(length)]
        print("正在写入数据：", data_float)
        slave.write_float(1, "0", data_float)
        await asyncio.sleep(0.3)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
