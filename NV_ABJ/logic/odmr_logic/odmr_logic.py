from qudi.core.module import LogicBase, Base
from qudi.core.connector import Connector

# GUI module declaration in e.g. qudi/gui/my_gui_module.py
class OdmrGui(Base):
    """ Description goes here """
      
    # Connector to get a reference to the measurement logic module
    _logic_connector = Connector(interface='OdmrLogic', name='odmr_logic')
    ...
    
    def on_activate(self):
        self.sigStartMeasurement.connect(self._logic_connector().start_measurement)
        self._logic_connector().sigMeasurementFinished.connect(self._measurement_finished)
        
    def trigger_measurement_start(self):
        """ Will just emit the sigStartMeasurement signal """
        self.sigStartMeasurement.emit()

    def _measurement_finished(self):
        """ Callback for measurement finished signal from logic module """
        print('Logic has finished the measurement')

    ...

# Logic module declaration in e.g. qudi/logic/my_logic_module.py
class OdmrLogic(LogicBase):
    """ Description goes here """
    _signal_generator = Connector(name='signal_generator', interface='SignalGenerator')


    ...
        
    def start_measurement(self):
        """ API method to start a measurement """
        # Actually perform your measurement here and emit notification signal upon finishing
        self.sigMeasurementFinished.emit()

        ...