#!/usr/bin/env python3
from PyQt5.QtCore    import QTimer
from PyQt5.QtWidgets import (QAbstractSpinBox, QComboBox, QDoubleSpinBox, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
        QPushButton, QRadioButton, QVBoxLayout, QWidget)

# QWidget is the base class of all user interface objects, super returns a proxy object
# a QWidget without a parent is just a window

def unit_conversion_factor(fromUnit, toUnit):
    prefix = {'m': 1, 'u': 1e-3, 'n': 1e-6}
    timeInterval = {'hr': 1, 'min': 1/60, 'sec': 1/3600}
    equiv = lambda Unit: prefix[Unit[0]] / timeInterval[Unit.split('/')[1]]
    return equiv(fromUnit)/equiv(toUnit)
    
class Pump(QWidget):
    def __init__(self, pumpBackend, parent=None):
        super(Pump, self).__init__(parent)

        self.pump = pumpBackend
        self.setFlowRate, self.setFlowRateUnit = self.pump.get_flow_rate()

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
        self.flowSpinBox.setValue(self.setFlowRate)
        self.flowSpinBox.setMaximum(10000)
        self.flowSpinBox.setDecimals(3)
        self.flowRateUnit = QComboBox()
        self.flowRateUnit.setEditable(False)
        self.flowRateUnit.addItems(['nL/sec','uL/hr','uL/min','mL/hr','mL/min'])
        self.flowRateUnit.setCurrentText(self.setFlowRateUnit)

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
        if unit != self.setFlowRateUnit:
            convFactor = unit_conversion_factor(self.setFlowRateUnit, unit)
            value *= convFactor
            self.setFlowRate = value
            self.setFlowRateUnit = unit
            self.flowSpinBox.setValue(value)
            
        if unit == 'nL/sec':
            value*=3600/1000
            unit = 'uL/hr'
        self.pump.set_flow_rate(value, unit)
        self.update_status()
        
    def update_dia(self):
        value = self.syringeDiaSpinBox.value()
        self.pump.set_diameter(value)
        self.update_status()

class Controller(QWidget):
    def __init__(self, N=1, parent=None):
        super(Controller, self).__init__(parent)

        import interface
        pumpBackends = interface.initPumps('COM3',N)
        pumps = [Pump(i) for i in pumpBackends]

        timer = QTimer(self)
        for pump in pumps:
            timer.timeout.connect(pump.update_status)

        timer.start(1000)

        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(pumps[0])
        for pump in pumps[1:]:
            mainLayout.addWidget(divider)
            mainLayout.addWidget(pump)

        self.setLayout(mainLayout)
        self.setWindowTitle("Syringe Pump Controller")

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv) # Create an application

    window = Controller(2)
    window.show() # display the window on the screen and create an event loop

    sys.exit(app.exec_()) # ensures a clean exit freeing all memory when the exit() handler is called or the widget is destroyed
