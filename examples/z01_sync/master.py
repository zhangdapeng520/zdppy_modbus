from zdpapi_modbus import cst, modbus_tcp
import time
import random

master = modbus_tcp.TcpMaster("127.0.0.1", 5011)
master.set_timeout(5.0)
slave_id = 1

while True:
    # 读取数据
    values = master.execute(slave_id, cst.READ_HOLDING_REGISTERS, 0, 6)
    print("values:", values)
    # 写入数据
    address = 10
    values = [random.randint(10, 20) for _ in range(6)]
    master.execute(slave_id, cst.WRITE_MULTIPLE_REGISTERS,
                   address, output_value=values)
    # 1s执行一次
    time.sleep(1)
