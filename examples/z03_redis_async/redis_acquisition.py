"""
将两个scada的数据取出，存入到redis中
"""

import json
from zdpapi_modbus import Device, trans_int_to_float
import time
import json
import asyncio, redis

# 每台机组自己单独采集
device = Device(device_id = 1, address = 0, length = 48)

controls = {
    "acceleratedSpeedX": 1,
    "acceleratedSpeedY": 1,
    "power": 1,
    "power1": 1,
    "rotorspeed": 1,
    "temperature": 1,
    "test": 10,
    "winddirection": 1,
    "windspeed": 1,
    "workMode": 1,
    "write_test1": 1,
    "yawerror": 1,
    "yawerror1": 1,
    "winddirection1": 1,
    "yawposition": 1
}

variables = ["机舱X方向振动", "机舱Y方向振动", "电网有功功率",
             "有功功率", "风轮转速", "环境温度",
                     "测试", "瞬时风向", "瞬时风速",
                     "工作模式", "无功功率最大设定值", "1#风向仪瞬时风向",
                     "2#风向仪瞬时风向", "机舱外风向", "偏航方位角"]
names = [
    "acceleratedSpeedX", "acceleratedSpeedY", "power",
    "power1", "rotorspeed", "temperature",
    "test", "winddirection", "windspeed",
    "workMode", "write_test1", "yawerror",
    "yawerror1", "winddirection1", "yawposition"
    ]



async def run():
    while True:
        start = time.time()
        rdb = redis.Redis("127.0.0.1", 6379, 1)
        data = rdb.get(f"{device.device_id}_control_data")
        data = json.loads(data)
        print("采集到的聚合数据是：", data)
        
        raw = rdb.get(f"{device.device_id}_control_raw")
        raw = json.loads(raw)
        print("采集到的非聚合数据是：", raw)

        print(f"读取设备{device.device_id}耗时：", time.time() - start)

# asyncio.run(run())

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
