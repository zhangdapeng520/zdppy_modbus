from .hooks import call_hooks
from .modbus_rtu import RtuQuery
from .modbus_tcp import TcpMaster
from .utils import to_data


class RtuOverTcpMaster(TcpMaster):
    """Subclass of TcpMaster. Implements the Modbus RTU over TCP MAC layer"""

    def _recv(self, expected_length=-1):
        """Receive the response from the slave"""
        response = to_data('')
        length = 255
        while len(response) < length:
            rcv_byte = self._sock.recv(1)
            if rcv_byte:
                response += rcv_byte
            if expected_length >= 0 and len(response) >= expected_length:
                break
        retval = call_hooks("modbus_rtu_over_tcp.RtuOverTcpMaster.after_recv", (self, response))
        if retval is not None:
            return retval
        return response

    def _make_query(self):
        """Returns an instance of a Query subclass implementing the modbus RTU protocol"""
        return RtuQuery()
