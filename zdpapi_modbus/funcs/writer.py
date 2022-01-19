from ..libs.modbus_tk import  modbus_tcp
from typing import  List,Any

def write(address:int,values:List[int],slave:Any=1,func:int=16,host:str="127.0.0.1",port:int=8888):
    """
    写入数据

    @param address 要写入的地址
    @param values 要写入的数据
    @param slave 从站ID
    @param func 功能码，写入数据的功能码一般是16或者4
    @param host modbus服务的主机地址
    @param port modbus服务的端口号
    """
    # 创建master
    master = modbus_tcp.TcpMaster(host=host, port=port)
    master.execute(slave, func, address, output_value=values)

def read():
    """
    读取数据
    """