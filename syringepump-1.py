#!/usr/bin/env python3
from PyQt5.QtCore    import QTimer
from PyQt5.QtWidgets import (QAbstractSpinBox, QComboBox, QDoubleSpinBox, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
        QPushButton, QRadioButton, QVBoxLayout, QWidget)

# QWidget is the base class of all user interface objects, super returns a proxy object
# a QWidget without a parent is just a window

class pump(QWidget):
    def __init__(self, pumpBackend, parent=None):
        super(pump, self).__init__(parent)

        self.pump = pumpBackend

        statusLabel = QLabel('Status:')
        flowRateLabel = QLabel('Flow Rate:')
        
        self.status = QLabel('Disconnected')
        self.flowStatus = QLabel('Disconnected')

        syringeDiaLabel = QLabel('Syringe Diameter:')
        self.syringeDiaStatus = QLabel('Disconnected')

        self.runButton = QRadioButton("&Run")
        self.runButton.show()
        self.stopButton = QRadioButton("&Stop")
        self.stopButton.show()
        
        setFlowRateLabel = QLabel('Set Flow Rate:')
        self.flowSpinBox = QDoubleSpinBox()
        self.flowSpinBox.setValue(self.pump.get_flow_rate()[0])
        self.flowSpinBox.setMaximum(1000)
        self.flowSpinBox.setDecimals(3)
        self.flowRateUnit = QComboBox()
        self.flowRateUnit.setEditable(False)
        self.flowRateUnit.addItems(['uL/min','mL/min','uL/hr','mL/hr'])
        self.flowRateUnit.setCurrentText(self.pump.get_flow_rate()[1])

        setSyringeDiaLabel = QLabel('Syringe Diameter:')
        self.syringeDiaSpinBox = QDoubleSpinBox()
        self.syringeDiaSpinBox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.syringeDiaSpinBox.setValue(self.pump.get_diameter())
        self.syringeDiaSpinBox.setSuffix(" mm")
        self.syringeDiaSpinBox.setMaximum(45)
        self.syringeDiaSpinBox.setDecimals(3)

        self.runButton.clicked.connect(self.pump.start)
        self.runButton.clicked.connect(self.update_status)
        self.stopButton.clicked.connect(self.pump.stop)
        self.stopButton.clicked.connect(self.update_status)
        self.flowSpinBox.valueChanged.connect(self.update_flow)
        self.flowRateUnit.currentIndexChanged.connect(self.update_flow)
        self.syringeDiaSpinBox.valueChanged.connect(self.update_dia)

        statusLayout = QGridLayout()
        statusLayout.addWidget(statusLabel, 0, 0)
        statusLayout.addWidget(self.status, 0, 1)
        statusLayout.addWidget(flowRateLabel, 1, 0)
        statusLayout.addWidget(self.flowStatus, 1, 1)
        statusLayout.addWidget(syringeDiaLabel, 2, 0)
        statusLayout.addWidget(self.syringeDiaStatus, 2, 1)
    
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.runButton)
        buttonLayout.addWidget(self.stopButton)

        setFlowLayout = QHBoxLayout()
        setFlowLayout.addWidget(setFlowRateLabel)
        setFlowLayout.addWidget(self.flowSpinBox)
        setFlowLayout.addWidget(self.flowRateUnit)

        setSyringeDiaLayout = QHBoxLayout()
        setSyringeDiaLayout.addWidget(setSyringeDiaLabel)
        setSyringeDiaLayout.addWidget(self.syringeDiaSpinBox)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(statusLayout)
        mainLayout.addLayout(buttonLayout)
        mainLayout.addLayout(setFlowLayout)
        mainLayout.addLayout(setSyringeDiaLayout)

        self.setLayout(mainLayout)
        self.setWindowTitle('Pump {}'.format(self.pump.pumpN))
    
    def update_status(self):
        self.status.setText(self.pump.get_status())
        
        value, unit = self.pump.get_flow_rate()
        self.flowStatus.setText('{:.4f} {}'.format(value, unit))

        dia = self.pump.get_diameter()
        self.syringeDiaStatus.setText('{:.3f} mm'.format(dia))

    def update_flow(self):
        value, unit = self.flowSpinBox.value(), self.flowRateUnit.currentText()
        self.pump.set_flow_rate(value, unit)
        self.update_status()

    def update_dia(self):
        value = self.syringeDiaSpinBox.value()
        self.pump.set_diameter(value)
        self.update_status()

class Controller(QWidget):
    def __init__(self, parent=None):
        super(Controller, self).__init__(parent)

        import interface
        pumpBackends = interface.initPumps('COM3',1)
        pump0 = pump(pumpBackends[0])

        timer = QTimer(self)
        timer.timeout.connect(pump0.update_status)
        timer.start(1000)

        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(pump0)

        self.setLayout(mainLayout)
        self.setWindowTitle("Syringe Pump Controller")

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv) # Create an application

    window = Controller()
    window.show() # display the window on the screen and create an event loop

    sys.exit(app.exec_()) # ensures a clean exit freeing all memory when the exit() handler is called or the widget is destroyed
