"""
将两个scada的数据取出，存入到redis中
"""

import json
from zdpapi_modbus import Device, trans_int_to_float
import time
import asyncio, redis, json

# 获取80台机组的转速
params = {
    "device_ids": list(range(1, 81)),
    "control_names": ["rotorspeed", ]
}

async def run():
    while True:
        start = time.time()
        rdb = redis.Redis("127.0.0.1", 6379, 1)
        data = {}
        if params["device_ids"]:
            for id in params["device_ids"]:
                item = rdb.get(f"{id}_control_data")
                json_data = json.loads(item)
                data[id] = {}
                data[id]["control"] = {}
                if params["control_names"]:
                    for control in params["control_names"]:
                        data[id]["control"][control] = json_data.get(control)
        print("采集到的聚合数据是：", data)
        print(f"获取数据耗时：", time.time() - start)

# asyncio.run(run())

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
