# zdpapi_modbus
python版modbus协议快速开发工具库

## 一、快速入门

### 1.1 实例1：读写数据

#### 1.1.1 slave读写master数据
```python
from zdpapi_modbus import  cst, modbus_tcp
import time
import random

# 创建一个TCP服务
server = modbus_tcp.TcpServer()
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
```

#### 1.1.2 master从slave读数据
```python
from zdpapi_modbus import cst, modbus_tcp
import time
import random

master = modbus_tcp.TcpMaster()
master.set_timeout(5.0)
slave_id = 1

while True:
    # 读取数据
    values = master.execute(slave_id, cst.READ_HOLDING_REGISTERS, 0, 6)
    print("values:", values)
    # 写入数据
    address = 10
    values = [random.randint(10, 20) for _ in range(6)]
    master.execute(slave_id, cst.WRITE_MULTIPLE_REGISTERS, address, output_value=values)
    # 1s执行一次
    time.sleep(1)
```

### 1.2 使用钩子

#### 1.2.1 slave
```python
import sys
from zdpapi_modbus import cst, modbus_tcp, utils
import logging


def main():
    logger = utils.create_logger(name="console", record_format="%(message)s")

    try:
        # 创建一个TCP服务
        server = modbus_tcp.TcpServer()
        logger.info("running...")
        logger.info("enter 'quit' for closing the server")
        # 启动server
        server.start()
        # 添加一个slave
        slave_1 = server.add_slave(1)
        # 添加一个block
        slave_1.add_block('0', cst.HOLDING_REGISTERS, 0, 100)
        while True:
            cmd = sys.stdin.readline()
            args = cmd.split(' ')
            # 退出
            if cmd.find('quit') == 0:
                sys.stdout.write('bye-bye\r\n')
                break
            # 添加slave
            elif args[0] == 'add_slave':
                slave_id = int(args[1])
                server.add_slave(slave_id)
                sys.stdout.write('done: slave %d added\r\n' % slave_id)
            # 添加block
            elif args[0] == 'add_block':
                slave_id = int(args[1])
                name = args[2]
                block_type = int(args[3])
                starting_address = int(args[4])
                length = int(args[5])
                slave = server.get_slave(slave_id)
                slave.add_block(name, block_type, starting_address, length)
                sys.stdout.write('done: block %s added\r\n' % name)
            # 写入数据
            elif args[0] == 'set_values':
                slave_id = int(args[1])
                name = args[2]
                address = int(args[3])
                values = []
                for val in args[4:]:
                    values.append(int(val))
                slave = server.get_slave(slave_id)
                slave.set_values(name, address, values)
                values = slave.get_values(name, address, len(values))
                sys.stdout.write('done: values written: %s\r\n' % str(values))
            # 读取数据
            elif args[0] == 'get_values':
                slave_id = int(args[1])
                name = args[2]
                address = int(args[3])
                length = int(args[4])
                slave = server.get_slave(slave_id)
                values = slave.get_values(name, address, length)
                sys.stdout.write('done: values read: %s\r\n' % str(values))
            else:
                sys.stdout.write("unknown command %s\r\n" % args[0])
    finally:
        server.stop()


if __name__ == "__main__":
    main()
```

#### 1.2.2 master
```python
from __future__ import print_function

from zdpapi_modbus import cst, modbus_tcp, hooks, utils, modbus
import logging


def main():
    """main"""
    logger = utils.create_logger("console", level=logging.DEBUG)
    # 读取数据之后的回调
    def on_after_recv(data):
        master, bytes_data = data
        logger.info(bytes_data)
    # 注册回调
    hooks.install_hook('modbus.Master.after_recv', on_after_recv)

    try:
        # 连接之前的回调
        def on_before_connect(args):
            master = args[0]
            logger.debug("on_before_connect {0} {1}".format(master._host, master._port))
        # 注册回调
        hooks.install_hook("modbus_tcp.TcpMaster.before_connect", on_before_connect)
        # 读取数据之后的回调
        def on_after_recv(args):
            response = args[1]
            logger.debug("on_after_recv {0} bytes received".format(len(response)))
        hooks.install_hook("modbus_tcp.TcpMaster.after_recv", on_after_recv)

        # 连接到slave
        master = modbus_tcp.TcpMaster()
        master.set_timeout(5.0)
        logger.info("connected")
        # 读取数据
        logger.info(master.execute(1, cst.READ_HOLDING_REGISTERS, 0, 3))

        # logger.info(master.execute(1, cst.READ_HOLDING_REGISTERS, 0, 2, data_format='f'))

        # Read and write floats
        # master.execute(1, cst.WRITE_MULTIPLE_REGISTERS, starting_address=0, output_value=[3.14], data_format='>f')
        # logger.info(master.execute(1, cst.READ_HOLDING_REGISTERS, 0, 2, data_format='>f'))

        # send some queries
        # logger.info(master.execute(1, cst.READ_COILS, 0, 10))
        # logger.info(master.execute(1, cst.READ_DISCRETE_INPUTS, 0, 8))
        # logger.info(master.execute(1, cst.READ_INPUT_REGISTERS, 100, 3))
        # logger.info(master.execute(1, cst.READ_HOLDING_REGISTERS, 100, 12))
        # logger.info(master.execute(1, cst.WRITE_SINGLE_COIL, 7, output_value=1))
        # logger.info(master.execute(1, cst.WRITE_SINGLE_REGISTER, 100, output_value=54))
        # logger.info(master.execute(1, cst.WRITE_MULTIPLE_COILS, 0, output_value=[1, 1, 0, 1, 1, 0, 1, 1]))
        # logger.info(master.execute(1, cst.WRITE_MULTIPLE_REGISTERS, 100, output_value=xrange(12)))

    except modbus.ModbusError as exc:
        logger.error("%s- Code=%d", exc, exc.get_exception_code())


if __name__ == "__main__":
    main()
```

