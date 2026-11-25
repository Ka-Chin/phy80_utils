import asyncio
import sys

from pymodbus.server import ModbusTcpServer
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QPushButton,
                               QVBoxLayout, QWidget)
from qasync import QEventLoop, asyncSlot

from modbot.gd81 import register_map as gd81_register_map
from modbot.moddev import create_modbus_dev


class Application:
    def __init__(self):
        self.servers: list[ModbusTcpServer] = []

    async def start(self):
        print("Starting Modbus servers...")

        server = create_modbus_dev("10.1.2.2", 5020, gd81_register_map)

        self.servers.append(server)

        await server.serve_forever(background=True)

    async def stop(self):
        print("Stopping Modbus servers...")

        for x in self.servers:
            await x.shutdown()


class MainWindow(QMainWindow):

    def __init__(self, app_logic: Application):
        super().__init__()

        self.app_logic: Application = app_logic

        self.setWindowTitle("Modbus Simulator")

        self.status: QLabel = QLabel("Stopped")

        self.start_button: QPushButton = QPushButton("Start")
        self.stop_button: QPushButton = QPushButton("Stop")

        layout = QVBoxLayout()
        layout.addWidget(self.status)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.start_button.clicked.connect(self.start_server)
        self.stop_button.clicked.connect(self.stop_server)

    @asyncSlot()
    async def start_server(self):
        await self.app_logic.start()
        self.status.setText("Running")

    @asyncSlot()
    async def stop_server(self):
        await self.app_logic.stop()
        self.status.setText("Stopped")


async def main(_app):
    app_logic = Application()
    window = MainWindow(app_logic)

    window.resize(400, 200)
    window.show()

    await asyncio.Event().wait()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    with loop:
        loop.run_until_complete(main(app))
