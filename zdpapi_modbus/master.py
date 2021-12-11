"""
master角色
"""
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

    def read_many_float(self, slave_id: int, data_length: int, keep_num: int = 2):
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

    def run_read_many_float(self, slave_id: int, data_length: int, keep_num: int = 2, freq_second: int = 1, console:bool=False):
        """
        批量读取float类型的数据
        """
        while True:
            data = self.read_many_float(slave_id, data_length, keep_num)
            if console:
                print(data)
            time.sleep(freq_second)
