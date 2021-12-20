## slave
模拟两个slave，每个slave负责提供50个机组的数据，每个机组有25个主控变量，其中有主控变量是高频数据

## redis
将modbus的数据采集，结构化存储到redis中。由于直接可用，不需要查询和修改，所以采用最简单的kv形式。

有两个key：
- `f"{self.device_id}_control_raw"`：存储的是对应机组的非聚合数据。值是json字符串，由{主控变量：[值]}组成，由于值可能是高频数据，所以是一个数组。
- `f"{self.device_id}_control_data"`：存储的是对应机组的聚合数据。值是json字符串，有{主控变量：值}组成，值都是取的高频数据中值数组的平均数。

期望在使用的时候，直接通过机组对应的机组ID，就能够拿到最新的所有的主控数据。

## redis acquisition
模拟的是数采服务


## redis socketio
模拟的是通讯服务

