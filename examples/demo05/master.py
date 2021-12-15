"""
从服务端获取100台机组的数据，每台机组有25个变量
"""
from zdpapi_modbus import Master
import time

master = Master("127.0.0.1", 502)
slave_id = 1

while True:
    data = master.read(1, 3, 0, 5000)
    print(master.to_float(data))
    time.sleep(1)
