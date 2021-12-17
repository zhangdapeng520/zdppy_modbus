"""
按照1秒钟传递100台机组的数据，1台机组25个变量
"""

from zdpapi_modbus import Slave, rand_float
import time

slave = Slave()
slave.add_slave(1)
slave.add_block(1, "0", 3, 0, 6000)

# 生成随机数
slave.start()

while True:
    data_float = list(range(2500))
    print("正在写入数据：", data_float)
    slave.write_float(1, "0", data_float)
    time.sleep(1)
