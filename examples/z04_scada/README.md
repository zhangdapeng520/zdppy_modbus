# 读取SCADA的mobbus数据存入到Redis中

## 启动方式
```shell
python main.py 1 50 127.0.0.1 5011
```

参数说明：
- 参数1：设备起始ID
- 参数2：设备结束ID
- 参数3：modbus 主机地址
- 参数4：modbus 端口号


