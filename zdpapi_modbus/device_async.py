
from .master_async import MasterAsync, trans_int_to_float
import time
import json
import asyncio
import aioredis

slave_id = 1


class DeviceAsync:
    def __init__(self, *, modbus_ip: str = "127.0.0.1", modbus_port:int = 502,  device_id, address, length) -> None:
        self.device_id = device_id
        self.master = MasterAsync(modbus_ip, modbus_port)
        self.address = address
        self.length = length
        self.redis = None  # redis连接

    async def connect_redis(self, redis_ip:int = "127.0.0.1", redis_port:int=6379, redis_db:int = 1):
        """
        连接到Redis
        """
        if self.redis is None:
            address = f"redis://{redis_ip}:{redis_port}/{redis_db}"
            self.redis = await aioredis.from_url(address)

    async def write_to_redis(self, *, redis_ip: int = "127.0.0.1", redis_port: int = 6379, redis_db: int = 1, controls, freeq_seconds: int = 0.04, debug: bool = False):
        """
        从modbus读取数据
        
        controls：{主控名称：该变量在modbus上的字节数}
        """
        await self.connect_redis(redis_ip=redis_ip, redis_port=redis_port, redis_db=redis_db)

        start = time.time()
        # 从modbus读取数据
        await asyncio.sleep(freeq_seconds)
        data = []
        # print("正在采集：", 1, 3, self.address, self.length)
        try:
            data = await self.master.execute(1, 3, self.address, self.length)
        except Exception as e:
            print(e)
        # print("采集到的原始数据是什么：", data)
        
        values = trans_int_to_float(data)

        self.raw = {}  # 聚合数据
        self.data_ = {}  # 非聚合数据

        def mean(value_list):
            """取平均数"""
            if value_list is None or len(value_list) == 0:
                return 0
            
            sum = 0
            for i in value_list:
                sum += i
            return sum / len(value_list)

        count = 0
        for k, v in controls.items():
            # 从队列中取数
            self.raw[k] = values[count: count + v]
            self.data_[k] = mean(values[count: count + v])
            count += v  # 浮点数一次进2个字节

        # 存入Redis
        await self.redis.set(f"{self.device_id}_control_raw", json.dumps(self.raw))
        await self.redis.set(f"{self.device_id}_control_data", json.dumps(self.data_))

        if debug:
            end = time.time()
            print("单次读取耗时: ", end - start)
            print(f"设备{self.device_id}采集到的数据是什么：", self.data_)
            print(f"设备{self.device_id}采集到的高频数据是什么：", self.raw)
            
        return self.raw, self.data_
