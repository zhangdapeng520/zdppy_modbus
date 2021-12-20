"""
按照0.5秒钟传递50台机组的数据，1台机组25个变量


"""

from zdpapi_modbus import Slave, rand_float
import time, sys

port = int(sys.argv[1])

slave = Slave("0.0.0.0", port)
slave.add_slave(1)
slave.add_block(1, "0", 3, 0, 3000)

# 生成随机数
slave.start()

while True:
    data_float = list(range(1250))
    print("正在写入数据：", data_float)
    slave.write_float(1, "0", data_float)
    time.sleep(0.5)
