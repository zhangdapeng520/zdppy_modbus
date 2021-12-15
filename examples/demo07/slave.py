from zdpapi_modbus import cst, modbus_tcp

SEREVR = modbus_tcp.TcpServer(address="0.0.0.0", port=504)

for i in range(1, 11):
    slave = SEREVR.add_slave(i)
    slave.add_block("data", cst.HOLDING_REGISTERS, 1, 150)
    slave.set_values("data", 1, [1234, 0, 0, 1])

SEREVR.start()
