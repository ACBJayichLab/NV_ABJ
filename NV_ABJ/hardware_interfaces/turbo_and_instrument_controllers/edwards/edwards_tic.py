"""https://gitlab.com/codingcoffeebean/edwardsserial/-/blob/develop/edwardsserial/serial_protocol.py?ref_type=heads
"""

import logging

import re
from warnings import warn

import serial

log = logging.getLogger(__name__)


class AlertID(Warning):
    ALERT_ID = {
        0: "No Alert",
        1: "ADC Fault",
        2: "ADC Not Ready",
        3: "Over Range",
        4: "Under Range",
        5: "ADC Invalid",
        6: "No Gauge",
        7: "Unknown",
        8: "Not Supported",
        9: "New ID",
        10: "Over Range",
        11: "Under Range",
        12: "Over Range",
        13: "Ion Em Timeout",
        14: "Not Struck",
        15: "Filament Fail",
        16: "Mag Fail",
        17: "Striker Fail",
        18: "Not Struck",
        19: "Filament Fail",
        20: "Cal Error",
        21: "Initialising",
        22: "Emission Error",
        23: "Over Pressure",
        24: "ASG Cant Zero",
        25: "RampUp Timeout",
        26: "Droop Timeout",
        27: "Run Hours High",
        28: "SC Interlock",
        29: "ID Volts Error",
        30: "Serial ID Fail",
        31: "Upload Active",
        32: "DX Fault",
        33: "Temp Alert",
        34: "SYSI Inhibit",
        35: "Ext Inhibit",
        36: "Temp Inhibit",
        37: "No Reading",
        38: "No Message",
        39: "NOV Failure",
        40: "Upload Timeout",
        41: "Download Failed",
        42: "No Tube",
        43: "Use Gauges 4-6",
        44: "Degas Inhibited",
        45: "IGC Inhibited",
        46: "Brownout/Short",
        47: "Service due",
    }

    def __init__(self, alert_id):
        message = f"{alert_id} ({self.ALERT_ID.get(alert_id)})"
        super().__init__(message)
        # self.id = alert_id


class ErrorResponse(Exception):

    ERROR_CODES = {
        1: "Invalid command for object ID",
        2: "Invalid query/command",
        3: "Missing parameter",
        4: "Parameter out of range",
        5: "Invalid command in current state - e.g. serial command to start or stop when in parallel control mode",
        6: "Data checksum error",
        7: "EEPROM read or write error",
        8: "Operation took too long",
        9: "Invalid config ID",
    }

    def __init__(self, error_code):
        message = f"Device responded with error code {error_code}: {self.ERROR_CODES.get(int(error_code))}"
        super().__init__(message)


class SerialProtocol:
    BAUDRATE = 9600
    COMMAND = re.compile(r"![CS]\d{1,5} (.+;?)+\r", flags=re.ASCII)
    SETUP_QUERY = re.compile(r"\?[S]\d{1,5}( \d+)*\r", flags=re.ASCII)
    VALUE_QUERY = re.compile(r"\?[V]\d{1,5}\r", flags=re.ASCII)
    MESSAGE = re.compile(
        f"{COMMAND.pattern}|{SETUP_QUERY.pattern}|{VALUE_QUERY.pattern}"
    )

    ERROR_RESPONSE = re.compile(
        r"\*[CSV]\d{1,5} (?P<error_code>\d{1,2})\r", flags=re.ASCII
    )
    DATA_RESPONSE = re.compile(r"=[SV]\d{1,5} (?P<data>.+;?)+\r", flags=re.ASCII)
    RESPONSE = re.compile(f"{ERROR_RESPONSE.pattern}|{DATA_RESPONSE.pattern}")

    STATE = {
        0: "Off State",
        1: "Off Goiing On State",
        2: "On Going Off Shutdown State",
        3: "On Going Off Normal State",
        4: "On State",
    }

    def __init__(self, port: str):
        self.port = port

    def _check_alert(self, object_id):
        *values, alert_id, priority = self.send_message("?V", object_id)
        alert_id = int(alert_id)
        if alert_id:
            warn(AlertID(alert_id))
        return values

    @classmethod
    def _create_message(cls, operation: str, object_id: int, data=None) -> str:
        data = f" {data}" if data is not None else ""
        message = f"{operation}{object_id}{data}\r"
        if not cls.MESSAGE.match(message):
            raise ValueError(
                f"Serial message {message.encode('unicode-escape')!r} does not have the correct format of {cls.MESSAGE}."
            )
        return message

    def send_message(self, operation, object_id, data=None):
        message = self._create_message(operation, object_id, data=data)
        with serial.serial_for_url(self.port, timeout=1, baudrate=self.BAUDRATE) as ser:
            ser.write(message.encode("ascii"))
            response = ser.read_until(b"\r").decode("ascii")
        log.debug(f"send_message: response={response}")
        response = self.RESPONSE.match(response)
        if not response:
            raise ConnectionError("No serial connection to device.")
        groups = response.groupdict()
        error_code = groups.get("error_code")
        if error_code:
            error_code = int(error_code)
            if error_code:
                raise ErrorResponse(error_code=error_code)
            return
        return groups.get("data").split(";")

ed = SerialProtocol("COM5")
print(ed._check_alert(904))