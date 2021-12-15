import asyncio
import time
from zdpapi_modbus import MasterAsync, cst


class Device:
    def __init__(self, slave_id):
        hostaddr = "127.0.0.1"
        port = 504
        self.slave_id = slave_id
        self.MASTER = MasterAsync(host=hostaddr, port=port)

    async def execute(self):
        data = await self.MASTER.execute(slave=int(self.slave_id), function_code=cst.READ_HOLDING_REGISTERS,
                                         starting_address=1,
                                         quantity_of_x=4)
        return data

    async def run(self):
        a = time.time()
        data = await self.execute()
        print("data: ", data)
        print(
            f"{self.slave_id} 单次采样耗时{round(time.time() - a,4)}秒 , 数值为 {data[0]} 数据长度为 {len(data)}")


Devices = [Device(i) for i in range(1, 11)]


async def collection():
    while 1:
        a = time.time()
        funcs = []
        for device in Devices:
            funcs.append(device.run())
        if len(funcs):
            await asyncio.gather(*funcs)
        print(f"全部采集{round(time.time() - a,4)}秒")

loop = asyncio.get_event_loop()
loop.run_until_complete(collection())
