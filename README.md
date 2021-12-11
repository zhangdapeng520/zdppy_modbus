# zdpapi_modbus
python版modbus协议快速开发工具库

安装方式
```shell
pip install zdpapi_modbus
```

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

### 1.3 批量写入和批量读取modbus

### 1.3.1 slave
```python
"""
按照1秒钟传递100台机组的数据，1台机组25个变量
"""

from zdpapi_modbus import cst, modbus_tcp, rand_float, trans_float_to_int
import time

# 创建一个TCP服务
server = modbus_tcp.TcpServer()

# 启动server
server.start()

# 添加一个slave
slave_id = 1
slave_1 = server.add_slave(slave_id)

# 添加一个block
block_name = "0"
slave_1.add_block(block_name, cst.HOLDING_REGISTERS, 0, 3000)

# 单台风机的数据
variables = [
    "机舱X方向振动",
    "机舱Y方向振动",
    "限功率运行状态",
    "电网有功功率",
    "有功功率",
    "风轮转速",
    "环境温度",
    "瞬时风向",
    "瞬时风速",
    "工作模式",
    "测试写入主控变量1",
    "1#风向仪瞬时风向",
    "2#风向仪瞬时风向",
    "机舱外风向",
    "偏航方位角",
    "测试（高频数据）1",
    "测试（高频数据）2",
    "测试（高频数据）3",
    "测试（高频数据）4",
    "测试（高频数据）5",
    "测试（高频数据）6",
    "测试（高频数据）7",
    "测试（高频数据）8",
    "测试（高频数据）9",
    "测试（高频数据）10",
]

# 分两个slave传，一个传50台风机
# 生成数据
data = []
address = 0
for i in range(1, 51):
    for j in range(1, len(variables)+1):
        control = {}
        control["device_id"] = i
        control["cname"] = variables[j-1]
        control["name"] = f"v{i}_{j}"
        address += 2
        control["address"] = address
        control["length"] = 2
        control["func"] = 3
        control["type"] = "F"
        data.append(control)

# 生成随机数
data_float = [rand_float(0, 100) for _ in data]

# 不断的写入数据
while True:
    # 生成数据

    # 写入数据
    slave = server.get_slave(slave_id)  # slave
    address = 0

    values = trans_float_to_int(data_float)
    value_length = len(values)
    print("要传输的数据个数：", value_length)
    index = 0
    while True:
        slave.set_values(block_name, index, values[index:index + 100])
        
        # 最后一次传输
        value_length -= 100
        if value_length <= 100:
            slave.set_values(block_name, index, values[index:])
            break
        
        # 每次传100个数
        index += 100

    time.sleep(1)
```

### 1.3.2 master
```python
"""
从服务端获取100台机组的数据，每台机组有25个变量
"""
from zdpapi_modbus import cst, modbus_tcp, trans_int_to_float
import time
import random

master = modbus_tcp.TcpMaster()
master.set_timeout(5.0)
slave_id = 1


# 单台风机的数据
variables = [
    "机舱X方向振动",
    "机舱Y方向振动",
    "限功率运行状态",
    "电网有功功率",
    "有功功率",
    "风轮转速",
    "环境温度",
    "瞬时风向",
    "瞬时风速",
    "工作模式",
    "测试写入主控变量1",
    "1#风向仪瞬时风向",
    "2#风向仪瞬时风向",
    "机舱外风向",
    "偏航方位角",
    "测试（高频数据）1",
    "测试（高频数据）2",
    "测试（高频数据）3",
    "测试（高频数据）4",
    "测试（高频数据）5",
    "测试（高频数据）6",
    "测试（高频数据）7",
    "测试（高频数据）8",
    "测试（高频数据）9",
    "测试（高频数据）10",
]

# 分两个slave传，一个传50台风机
# 生成数据
data = []
address = 0
for i in range(1, 51):
    for j in range(1, len(variables)+1):
        control = {}
        control["device_id"] = i
        control["cname"] = variables[j-1]
        control["name"] = f"v{i}_{j}"
        address += 2
        control["address"] = address
        control["length"] = 2
        control["func"] = 3
        control["type"] = "F"
        data.append(control)

while True:
    # 读取数据
    data = []
    data_length = 2500  # 要取出2500个数
    index = 0
    while True:
        # 每次取出100个数
        length = 100
        values = master.execute(
            slave_id, cst.READ_HOLDING_REGISTERS, index, length)
        data.extend(values)

        # 最后一次取
        data_length -= 100
        if data_length <= 100:
            values = master.execute(
                slave_id, cst.READ_HOLDING_REGISTERS, index, data_length)
            data.extend(values)
            break

        index += 100

    # print("data:", data, len(data))

    # 解析为真实的数组
    result = trans_int_to_float(data, keep_num=2)
    print("最终结果：", result, len(result))

    # 1s执行一次
    time.sleep(1)
```

### 1.4 使用Slave和Master类
#### 1.4.1 slave
```python
"""
按照1秒钟传递100台机组的数据，1台机组25个变量
"""

from zdpapi_modbus import Slave, rand_float

slave = Slave()
slave.add_slave(1)
slave.add_block(1, "0", 3)

# 单台风机的数据
variables = [
    "机舱X方向振动",
    "机舱Y方向振动",
    "限功率运行状态",
    "电网有功功率",
    "有功功率",
    "风轮转速",
    "环境温度",
    "瞬时风向",
    "瞬时风速",
    "工作模式",
    "测试写入主控变量1",
    "1#风向仪瞬时风向",
    "2#风向仪瞬时风向",
    "机舱外风向",
    "偏航方位角",
    "测试（高频数据）1",
    "测试（高频数据）2",
    "测试（高频数据）3",
    "测试（高频数据）4",
    "测试（高频数据）5",
    "测试（高频数据）6",
    "测试（高频数据）7",
    "测试（高频数据）8",
    "测试（高频数据）9",
    "测试（高频数据）10",
]

# 分两个slave传，一个传50台风机
# 生成数据
data = []
address = 0
for i in range(1, 51):
    for j in range(1, len(variables)+1):
        control = {}
        control["device_id"] = i
        control["cname"] = variables[j-1]
        control["name"] = f"v{i}_{j}"
        address += 2
        control["address"] = address
        control["length"] = 2
        control["func"] = 3
        control["type"] = "F"
        data.append(control)

# 生成随机数
data_float = [rand_float(0, 100) for _ in data]
slave.run(1, "0", data_float, random_data=True)
```

#### 1.4.2 master
```python
"""
从服务端获取100台机组的数据，每台机组有25个变量
"""
from zdpapi_modbus import Master

master = Master()
slave_id = 1


# 单台风机的数据
variables = [
    "机舱X方向振动",
    "机舱Y方向振动",
    "限功率运行状态",
    "电网有功功率",
    "有功功率",
    "风轮转速",
    "环境温度",
    "瞬时风向",
    "瞬时风速",
    "工作模式",
    "测试写入主控变量1",
    "1#风向仪瞬时风向",
    "2#风向仪瞬时风向",
    "机舱外风向",
    "偏航方位角",
    "测试（高频数据）1",
    "测试（高频数据）2",
    "测试（高频数据）3",
    "测试（高频数据）4",
    "测试（高频数据）5",
    "测试（高频数据）6",
    "测试（高频数据）7",
    "测试（高频数据）8",
    "测试（高频数据）9",
    "测试（高频数据）10",
]

# 分两个slave传，一个传50台风机
# 生成数据
data = []
address = 0
for i in range(1, 51):
    for j in range(1, len(variables)+1):
        control = {}
        control["device_id"] = i
        control["cname"] = variables[j-1]
        control["name"] = f"v{i}_{j}"
        address += 2
        control["address"] = address
        control["length"] = 2
        control["func"] = 3
        control["type"] = "F"
        data.append(control)

master.run_read_many_float(slave_id, 2500, console=True)
```


## 二、数据的打包和解包

### 2.1 基本使用
```python
from zdpapi_modbus import *

data = [11, 22, 33]
# 测试打包
print("============================================测试打包=====================================================")
print(pack_byte(data))
print(pack_int(data))
print(pack_long(data))
print(pack_float(data))
print(pack_double(data))
print("============================================测试完毕=====================================================\n\n")

# 测试解包
print("============================================测试解包=====================================================")
print(unpack_byte(len(data), pack_byte(data)))
print(unpack_int(len(data), pack_int(data)))
print(unpack_long(len(data), pack_long(data)))
print(unpack_float(len(data), pack_float(data)))
print(unpack_double(len(data), pack_double(data)))
print("============================================测试完毕=====================================================\n\n")
```

### 2.2 数据类型转换
```python
from zdpapi_modbus import *

data = [11.11, 22.22, 33.33]

# 将浮点数转换为整数，再将整数还原为浮点数
print(trans_float_to_int(data))
print(trans_int_to_float(trans_float_to_int(data)))
```

## 三、生成随机数

### 3.1 生成随机浮点数
```python
from zdpapi_modbus import *

data = [rand_float(0, 100) for _ in range(50)]
print(data)

# 将浮点数转换为整数，再将整数还原为浮点数
print(trans_float_to_int(data))
print(trans_int_to_float(trans_float_to_int(data), keep_num=6))
```
