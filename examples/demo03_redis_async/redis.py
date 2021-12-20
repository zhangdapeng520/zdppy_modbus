"""
将两个scada的数据取出，存入到redis中
"""

from zdpapi_modbus import Device
import sys, time, asyncio

# 开始设备和结束设备
device_id_start = int(sys.argv[1])
device_id_end = int(sys.argv[2])
modbus_ip = sys.argv[3]
modbus_port = int(sys.argv[4])

devices = [Device(modbus_ip=modbus_ip, modbus_port=modbus_port, device_id=i, address=(i - 1) % 50 * 48, length=48)
           for i in range(device_id_start, device_id_end+1)]

controls = { # 键是主控名称，值是float数值个数
        "acceleratedSpeedX":1, 
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

async def run():
    while True:
        # 每次读取50个
        start = time.time()
        tasks = []
        for device in devices:
            tasks.append(device.write_to_redis(controls=controls))
        await asyncio.gather(*tasks)
        await asyncio.sleep(0.3)
        print("总共读取耗时：", time.time() - start)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
