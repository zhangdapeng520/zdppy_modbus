"""
master角色
"""
from typing import Tuple
from .libs.modbus_tk import modbus_tcp
from .libs.modbus_tk import defines as cst
from .zstruct import trans_int_to_float
import time


class Master:
    def __init__(self,
                 host: str = "127.0.0.1",
                 port: int = 502,
                 timeout_in_sec: float = 5.0) -> None:
        self.master = modbus_tcp.TcpMaster(
            host=host, port=port, timeout_in_sec=timeout_in_sec)

    def read_float(self, slave_id: int, data_length: int, keep_num: int = 2):
        """
        批量读取float类型的数据
        """
        data = []
        index = 0
        while True:
            # 每次取出100个数
            length = 100
            values = self.master.execute(
                slave_id, cst.READ_HOLDING_REGISTERS, index, length)
            data.extend(values)

            # 最后一次取
            data_length -= 100
            if data_length <= 100:
                values = self.master.execute(
                    slave_id, cst.READ_HOLDING_REGISTERS, index, data_length)
                data.extend(values)
                break

            index += 100

        # 解析为真实的数组
        result = trans_int_to_float(data, keep_num=keep_num)
        return result

    
    def read(self, slave_id, func_code, address, length):
        """
        从modbus读取数据
        """
        # 超过124个了
        if length > 124:
            data = []
            while length > 124:
                temp = self.master.execute(slave_id, func_code, address, 124)
                data.extend(temp)
                address += 124
                length -= 124
            else: # 保证读取完毕
                temp = self.master.execute(slave_id, func_code, address, length)
                data.extend(temp)
            return data
        
        # 不超过则正常读取
        return self.master.execute(slave_id, func_code, address, length)

    def to_float(self, data: Tuple[int], keep_num: int = 2):
        """
        将整数类型的列表转换为浮点数类型的列表
        """
        result = trans_int_to_float(data, keep_num=keep_num)
        return result
