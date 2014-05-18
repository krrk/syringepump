#!/usr/bin/env python3
from PyQt5.QtCore    import QTimer
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QGridLayout, QPushButton, QRadioButton, QMainWindow,
                             QHBoxLayout, QVBoxLayout, QFrame)

# QWidget is the base class of all user interface objects, super returns a proxy object
# a QWidget without a parent is just a window

class pump(QWidget):
    def __init__(self, parent=None):
        super(pump, self).__init__(parent)
        
        from interface import Model44
        self.pump0 = Model44('/dev/tty.usbserial',0)
        self.pump1 = Model44('/dev/tty.usbserial',1)

        timer = QTimer(self)
        timer.timeout.connect(self.update_status)
        timer.start(1000)



        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)

        mainLayout = QGridLayout()
        NROWS, NCOLS = 3, 3 
        mainLayout.addLayout(statusLayout, 0, 0)
        mainLayout.addLayout(flowLayout, 1, 0)
        mainLayout.addLayout(runLayout, 2, 0)
        mainLayout.addWidget(divider,0,1,NROWS,1)
        
        #mainLayout.addWidget(statusLabel, 0, 0)
        #mainLayout.addWidget(self.statusLabel, 0, 1)
        #mainLayout.addWidget(self.runButton, 1, 0)
        #mainLayout.addWidget(self.stopButton, 1, 1)
        
        self.setLayout(mainLayout)
        self.setWindowTitle("Syringe Pump Controller")

    def pumpLayout(self, pump):
        statusLabel = QLabel('Status:')
        flowLabel = QLabel('Flow Rate:')
        
        self.statusLabel = QLabel('Disconnected')
        self.flowLabel = QLabel('Disconnected')

        self.runButton = QRadioButton("&Run")
        self.runButton.show()
        self.stopButton = QRadioButton("&Stop")
        self.stopButton.show()

        self.runButton.clicked.connect(self.pump.start)
        self.runButton.clicked.connect(self.update_status)
        self.stopButton.clicked.connect(self.pump.stop)
        self.stopButton.clicked.connect(self.update_status)

        Layout = QGridLayout()
        Layout.addWidget(statusLabel
        statusLayout = QHBoxLayout()
        statusLayout.addWidget(statusLabel)
        statusLayout.addWidget(self.statusLabel)

        flowLayout = QHBoxLayout()
        flowLayout.addWidget(flowLabel)
        flowLayout.addWidget(self.flowLabel)

        runLayout = QHBoxLayout()
        runLayout.addWidget(self.runButton)
        runLayout.addWidget(self.stopButton)

    def update_status(self):
        self.statusLabel.setText(self.pump0.get_status())
        
        rate, unit = self.pump0.get_flow_rate()
        self.flowLabel.setText('{:.4f} {}'.format(rate, unit))


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv) # Create an application

    window = pump()
    window.show() # display the window on the screen and create an event loop

    sys.exit(app.exec_()) # ensures a clean exit freeing all memory when the exit() handler is called or the widget is destroyed
