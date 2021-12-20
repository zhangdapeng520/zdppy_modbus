"""
将两个scada的数据取出，存入到redis中
"""

from zdpapi_modbus import DeviceAsync
import sys
import asyncio
from config import controls, redis_config

# 开始设备和结束设备
device_id_start = int(sys.argv[1])  # 设备起始ID
device_id_end = int(sys.argv[2])  # 设备结束ID（包含）
modbus_ip = sys.argv[3]  # scada上的modbus ip地址
modbus_port = int(sys.argv[4])  # scada上的modbus port端口号

# 创建设备
devices = [DeviceAsync(modbus_ip=modbus_ip, modbus_port=modbus_port, device_id=i, address=(i - 1) % 50 * 48, length=48)
           for i in range(device_id_start, device_id_end+1)]


async def run():
    while True:
        tasks = []
        # 读取所有的设备
        for device in devices:
            tasks.append(device.write_to_redis(redis_ip=redis_config.get("host"), redis_port=redis_config.get(
                "port"), redis_db=redis_config.get("db"), controls=controls, debug=True))
        await asyncio.gather(*tasks)
        await asyncio.sleep(0.3)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
