from zdpapi_modbus import cst, modbus_tcp
import time
import random

# 创建一个TCP服务
server = modbus_tcp.TcpServer(port=8888, address='0.0.0.0')
# 启动server
server.start()
# 添加一个slave
slave_id = 1
slave_1 = server.add_slave(slave_id)
# 添加一个block
block_name = "0"
slave_1.add_block(block_name, cst.HOLDING_REGISTERS, 0, 100)


# 不断的写入数据
while True:
    # 写入数据
    slave = server.get_slave(slave_id)
    address = 0
    values = [random.randint(0, 100) for _ in range(6)]
    slave.set_values(block_name, address, values)
    values = slave.get_values(block_name, address, len(values))
    print("slave上的values是：", values)
    # 读取数据
    slave = server.get_slave(slave_id)
    address = 10
    values = slave.get_values(block_name, address, len(values))
    print("slave接收到server传过来的数据：", values)
    time.sleep(1)
