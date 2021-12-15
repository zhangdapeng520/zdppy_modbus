import asyncio
import struct
from .libs.modbus_tk import defines
from .libs.modbus_tk import LOGGER
from .libs.modbus_tk.hooks import call_hooks
from .libs.modbus_tk.utils import to_data, get_log_buffer
from .libs.modbus_tk.exceptions import(
    ModbusError, ModbusFunctionNotSupportedError,  ModbusInvalidResponseError
)
from .libs.modbus_tk.modbus import Master
from .libs.modbus_tk import modbus_tcp
from typing import Tuple
from .zstruct import trans_int_to_float

class MasterAsync(Master):
    """
    异步的Master类
    """

    def __init__(self, host="127.0.0.1", port=502, timeout_in_sec=5.0):
        """
        host: 主机地址
        port: 端口号
        timeout_in_sec: 超时时间
        """
        super(MasterAsync, self).__init__(timeout_in_sec)
        self._host = host
        self._port = port
        self._reader = None
        self._writer = None

    async def open(self):
        """
        建立与slave的通讯
        """
        if not self._is_opened:
            await self._do_open()
            self._is_opened = True

    def close(self):
        """
        关闭与slave的通讯
        """
        if self._is_opened:
            ret = self._do_close()
            if ret:
                self._is_opened = False

    async def _do_open(self):
        """
        连接slave
        """
        if self._writer:
            self._writer.close()
        call_hooks("modbus_tcp.TcpMaster.before_connect", (self, ))
        try:
            self._reader, self._writer = await asyncio.open_connection(self._host, self._port)
        except:
            return False
        call_hooks("modbus_tcp.TcpMaster.after_connect", (self, ))
        return True

    def _do_close(self):
        """
        关闭与slave的连接
        """
        if self._writer:
            call_hooks("modbus_tcp.TcpMaster.before_close", (self, ))
            self._writer.close()
            call_hooks("modbus_tcp.TcpMaster.after_close", (self, ))
            self._reader = None
            self._writer = None
            return True

    async def _send(self, request):
        """
        向slave发送请求
        """
        retval = call_hooks(
            "modbus_tcp.TcpMaster.before_send", (self, request))
        if retval is not None:
            request = retval
        try:
            self._writer.write(request)
        except Exception as e:
            await asyncio.sleep(1)
            if self._verbose:
                LOGGER.debug(f"send data timeout {e}")

    async def _recv(self, expected_length=-1):
        """
        从slave接收请求
        """
        try:
            response = to_data('')
            length = 255
            while len(response) < length:
                rcv_byte = await self._reader.read(1)
                if rcv_byte:
                    response += rcv_byte
                    if len(response) == 6:
                        to_be_recv_length = struct.unpack(">HHH", response)[2]
                        length = to_be_recv_length + 6
                else:
                    break

            retval = call_hooks(
                "modbus_tcp.TcpMaster.after_recv", (self, response))
            if retval is not None:
                return retval

        except Exception as e:
            self._is_opened = False
            await asyncio.sleep(1)
            if self._verbose:
                LOGGER.debug(f"recv data timeout {e}")
        return response

    def _make_query(self):
        """
        tcp协议查询
        """
        return modbus_tcp.TcpQuery()

    async def execute(
            self, slave, function_code, starting_address, quantity_of_x=0, output_value=0, data_format="", expected_length=-1, write_starting_address_FC23=0):
        """
        从modbus执行请求，获取数据
        """
        pdu = ""
        is_read_function = False
        nb_of_digits = 0

        # open the connection if it is not already done
        await self.open()

        # Build the modbus pdu and the format of the expected data.
        # It depends of function code. see modbus specifications for details.
        if function_code == defines.READ_COILS or function_code == defines.READ_DISCRETE_INPUTS:
            is_read_function = True
            pdu = struct.pack(">BHH", function_code,
                              starting_address, quantity_of_x)
            byte_count = quantity_of_x // 8
            if (quantity_of_x % 8) > 0:
                byte_count += 1
            nb_of_digits = quantity_of_x
            if not data_format:
                data_format = ">" + (byte_count * "B")
            if expected_length < 0:
                # No length was specified and calculated length can be used:
                # slave + func + bytcodeLen + bytecode + crc1 + crc2
                expected_length = byte_count + 5

        elif function_code == defines.READ_INPUT_REGISTERS or function_code == defines.READ_HOLDING_REGISTERS:
            is_read_function = True
            pdu = struct.pack(">BHH", function_code,
                              starting_address, quantity_of_x)
            if not data_format:
                data_format = ">" + (quantity_of_x * "H")
            if expected_length < 0:
                # No length was specified and calculated length can be used:
                # slave + func + bytcodeLen + bytecode x 2 + crc1 + crc2
                expected_length = 2 * quantity_of_x + 5

        elif (function_code == defines.WRITE_SINGLE_COIL) or (function_code == defines.WRITE_SINGLE_REGISTER):
            if function_code == defines.WRITE_SINGLE_COIL:
                if output_value != 0:
                    output_value = 0xff00
                fmt = ">BHH"
            else:
                fmt = ">BH"+("H" if output_value >= 0 else "h")
            pdu = struct.pack(fmt, function_code,
                              starting_address, output_value)
            if not data_format:
                data_format = ">HH"
            if expected_length < 0:
                # No length was specified and calculated length can be used:
                # slave + func + adress1 + adress2 + value1+value2 + crc1 + crc2
                expected_length = 8

        elif function_code == defines.WRITE_MULTIPLE_COILS:
            byte_count = len(output_value) // 8
            if (len(output_value) % 8) > 0:
                byte_count += 1
            pdu = struct.pack(">BHHB", function_code,
                              starting_address, len(output_value), byte_count)
            i, byte_value = 0, 0
            for j in output_value:
                if j > 0:
                    byte_value += pow(2, i)
                if i == 7:
                    pdu += struct.pack(">B", byte_value)
                    i, byte_value = 0, 0
                else:
                    i += 1
            if i > 0:
                pdu += struct.pack(">B", byte_value)
            if not data_format:
                data_format = ">HH"
            if expected_length < 0:
                # No length was specified and calculated length can be used:
                # slave + func + adress1 + adress2 + outputQuant1 + outputQuant2 + crc1 + crc2
                expected_length = 8

        elif function_code == defines.WRITE_MULTIPLE_REGISTERS:
            if output_value and data_format:
                byte_count = struct.calcsize(data_format)
            else:
                byte_count = 2 * len(output_value)
            pdu = struct.pack(">BHHB", function_code,
                              starting_address, byte_count // 2, byte_count)
            if output_value and data_format:
                pdu += struct.pack(data_format, *output_value)
            else:
                for j in output_value:
                    fmt = "H" if j >= 0 else "h"
                    pdu += struct.pack(">" + fmt, j)
            # data_format is now used to process response which is always 2 registers:
            #   1) data address of first register, 2) number of registers written
            data_format = ">HH"
            if expected_length < 0:
                # No length was specified and calculated length can be used:
                # slave + func + adress1 + adress2 + outputQuant1 + outputQuant2 + crc1 + crc2
                expected_length = 8

        elif function_code == defines.READ_EXCEPTION_STATUS:
            pdu = struct.pack(">B", function_code)
            data_format = ">B"
            if expected_length < 0:
                # No length was specified and calculated length can be used:
                expected_length = 5

        elif function_code == defines.DIAGNOSTIC:
            # SubFuncCode  are in starting_address
            pdu = struct.pack(">BH", function_code, starting_address)
            if len(output_value) > 0:
                for j in output_value:
                    # copy data in pdu
                    pdu += struct.pack(">B", j)
                if not data_format:
                    data_format = ">" + (len(output_value) * "B")
                if expected_length < 0:
                    # No length was specified and calculated length can be used:
                    # slave + func + SubFunc1 + SubFunc2 + Data + crc1 + crc2
                    expected_length = len(output_value) + 6

        elif function_code == defines.READ_WRITE_MULTIPLE_REGISTERS:
            is_read_function = True
            byte_count = 2 * len(output_value)
            pdu = struct.pack(
                ">BHHHHB",
                function_code, starting_address, quantity_of_x, write_starting_address_FC23,
                len(output_value), byte_count
            )
            for j in output_value:
                fmt = "H" if j >= 0 else "h"
                # copy data in pdu
                pdu += struct.pack(">"+fmt, j)
            if not data_format:
                data_format = ">" + (quantity_of_x * "H")
            if expected_length < 0:
                # No lenght was specified and calculated length can be used:
                # slave + func + bytcodeLen + bytecode x 2 + crc1 + crc2
                expected_length = 2 * quantity_of_x + 5
        else:
            raise ModbusFunctionNotSupportedError(
                "The {0} function code is not supported. ".format(function_code))

        # instantiate a query which implements the MAC (TCP or RTU) part of the protocol
        query = self._make_query()

        # add the mac part of the protocol to the request
        request = query.build_request(pdu, slave)

        # send the request to the slave
        retval = call_hooks("modbus.Master.before_send", (self, request))
        if retval is not None:
            request = retval
        if self._verbose:
            LOGGER.debug(get_log_buffer("-> ", request))
        await self._send(request)

        call_hooks("modbus.Master.after_send", (self, ))

        if slave != 0:
            # receive the data from the slave
            response = await self._recv(expected_length)
            if len(response) == 0:
                LOGGER.exception(f"recv data timeout")
                return
            retval = call_hooks("modbus.Master.after_recv", (self, response))
            if retval is not None:
                response = retval
            if self._verbose:
                LOGGER.debug(get_log_buffer("<- ", response))

            # extract the pdu part of the response
            response_pdu = query.parse_response(response)

            # analyze the received data
            (return_code, byte_2) = struct.unpack(">BB", response_pdu[0:2])

            if return_code > 0x80:
                # the slave has returned an error
                exception_code = byte_2
                raise ModbusError(exception_code)
            else:
                if is_read_function:
                    # get the values returned by the reading function
                    byte_count = byte_2
                    data = response_pdu[2:]
                    if byte_count != len(data):
                        # the byte count in the pdu is invalid
                        raise ModbusInvalidResponseError(
                            "Byte count is {0} while actual number of bytes is {1}. ".format(
                                byte_count, len(data))
                        )
                else:
                    # returns what is returned by the slave after a writing function
                    data = response_pdu[1:]

                # returns the data as a tuple according to the data_format
                # (calculated based on the function or user-defined)
                result = struct.unpack(data_format, data)
                if nb_of_digits > 0:
                    digits = []
                    for byte_val in result:
                        for i in range(8):
                            if len(digits) >= nb_of_digits:
                                break
                            digits.append(byte_val % 2)
                            byte_val = byte_val >> 1
                    result = tuple(digits)
                return result

    async def read(self, slave_id, func_code, address, length):
        """
        从modbus读取数据
        """
        # 超过124个了
        if length > 124:
            data = []
            while length > 124:
                temp = await self.execute(slave_id, func_code, address, 124)
                data.extend(temp)
                address += 124
                length -= 124
            else:  # 保证读取完毕
                temp = await self.execute(
                    slave_id, func_code, address, length)
                data.extend(temp)
            return data

        # 不超过则正常读取
        data = await self.execute(slave_id, func_code, address, length)
        return data

    def to_float(self, data: Tuple[int], keep_num: int = 2):
        """
        将整数类型的列表转换为浮点数类型的列表
        """
        result = trans_int_to_float(data, keep_num=keep_num)
        return result
