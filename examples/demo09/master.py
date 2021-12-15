"""
从服务端获取100台机组的数据，每台机组有25个变量
"""
from zdpapi_modbus import MasterAsync
import time, asyncio

master = MasterAsync("127.0.0.1", 502)
slave_id = 1

class Device:
    def __init__(self, address, length) -> None:
        self.master = MasterAsync("127.0.0.1", 502)
        self.address = address
        self.length = length
    
    async def execute(self):
        self.master.execute(1, 3, self.address, self.length)

devices = [Device((i-1)*50, 50) for i in range(1, 101)]

async def run():
    while True:
        # 每次读取50个
        total_time = 0
        tasks = []
        for device in devices:
            start = time.time()
            tasks.append(device.execute())
            asyncio.sleep(0.04)
            end = time.time()
            spend = end - start
            print("单次读取耗时：", spend)
            total_time += spend
        await asyncio.gather(*tasks)
        print("总共读取耗时：", total_time)

# asyncio.run(run())

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
