import asyncio

from pymodbus.datastore import (ModbusDeviceContext, ModbusServerContext,
                                ModbusSparseDataBlock)
from pymodbus.server import ModbusTcpServer


def create_context(initial_value):
    device = ModbusDeviceContext(
        hr=ModbusSparseDataBlock(
            {
                0: [initial_value] * 100,
            }
        )
    )

    return ModbusServerContext(
        devices=device,
        single=True,
    )


async def main():
    # Server A
    context_a = create_context(0x1234)

    server_a = ModbusTcpServer(
        context_a,
        address=("127.0.0.1", 5020),
    )

    # Server B
    context_b = create_context(0x5678)

    server_b = ModbusTcpServer(
        context_b,
        address=("127.0.0.2", 5020),
    )

    print("Starting Modbus TCP servers...")

    await asyncio.gather(
        server_a.serve_forever(),
        server_b.serve_forever(),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Servers stopped.")
