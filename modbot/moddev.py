import asyncio
import typing as t

from pymodbus.server import ModbusTcpServer
from pymodbus.simulator import DataType, SimData, SimDevice

TYPE_MAP = {
    "INT16": DataType.INT16,
    "UINT16": DataType.UINT16,
    "INT32": DataType.INT32,
    "UINT32": DataType.UINT32,
    "FLOAT32": DataType.FLOAT32,
    "FLOAT64": DataType.FLOAT64,
}

DATA_ITEM = dict[str, int | str | list[int] | list[float]]


def build_simdata(item: DATA_ITEM):
    dtype: str = t.cast(str, item["type"])
    address: int = t.cast(int, item["address"]) - 40001
    value = item["value"]

    if dtype == "STRING":
        length: int = t.cast(int, item["length"])
        str_value: str = t.cast(str, item["value"])

        if len(str_value) > length:
            raise ValueError(f"String too long: {item}")

        str_value = str_value.ljust(length)

        return SimData(
            address=address,
            values=str_value,
            datatype=DataType.STRING,
            string_encoding="ascii",
        )

    return SimData(
        address=address,
        values=value,
        datatype=TYPE_MAP[dtype],
    )


def trace_packet(is_recv: bool, data: bytes) -> bytes:
    direction = "RX" if is_recv else "TX"
    print(f"[PACKET {direction}] {data.hex(' ')}")
    return data


def trace_pdu(is_recv: bool, pdu: t.Any) -> t.Any:  # pyright: ignore[reportAny]
    direction = "RX" if is_recv else "TX"
    print(f"[PDU {direction}] {pdu}")
    return pdu  # pyright: ignore[reportAny]


def create_modbus_dev(
    address: str, port: int, data: list[DATA_ITEM]
) -> ModbusTcpServer:
    device = SimDevice(
        id=1,
        simdata=[build_simdata(x) for x in data],
    )

    return ModbusTcpServer(
        device,
        address=(address, port),
        trace_packet=trace_packet,
        trace_pdu=trace_pdu,
    )
