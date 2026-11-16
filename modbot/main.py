import asyncio
import sys

from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QPushButton,
                               QVBoxLayout, QWidget)
from qasync import QEventLoop, asyncSlot


class Application:
    def __init__(self):
        self.servers = []

    async def start(self):
        print("Starting Modbus servers...")

        # Start your Modbus server tasks here
        await asyncio.sleep(0.1)

    async def stop(self):
        print("Stopping Modbus servers...")

        # Stop your Modbus servers here
        await asyncio.sleep(0.1)


class MainWindow(QMainWindow):

    def __init__(self, app_logic):
        super().__init__()

        self.app_logic = app_logic

        self.setWindowTitle("Modbus Simulator")

        self.status = QLabel("Stopped")

        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")

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


async def main(app):
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
