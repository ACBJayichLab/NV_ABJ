#############################################################################################
# Third party
import sys
import numpy as np
from dataclasses import dataclass
import matplotlib.pyplot as plt
import matplotlib
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from scipy.signal import find_peaks

# Classes for Typing
from NV_ABJ.abstract_interfaces.photon_counter import PhotonCounter

# Importing generated python code from qtpy ui
from NV_ABJ.user_interfaces.running_counts_widget.generated_ui import Ui_running_counts_widget
#############################################################################################
import time
class RunningCountsWidget(Ui_running_counts_widget):
    @dataclass
    class config:
        cursor_color:str = "black"
        maximum_cursor_color:str = "red"
        cursor_shape:str = "o"
        line_color:str = "orange"
        graph_dpi:int = 300
        dwell_time_ms:float = 5
        number_of_points:int = 200
        cursor_size:int = 1
        cursor_max_size:int = 2
        refresh_time_ms:float = 1000     


    # Asynchronous running of the confocal scanning 
    class Worker(QObject):
        finished = pyqtSignal()
        progress = pyqtSignal(int)

        def __init__(self,dwell_time_s:float,
                        photon_counter:PhotonCounter,
                        *args,**kwargs):
            
            super().__init__(*args,**kwargs)
            self.dwell_time_s = dwell_time_s
            self.photon_counter = photon_counter
            self.counts = None

        def run(self):
            with self.photon_counter as pc:
                self.counts = pc.get_counts_per_second(dwell_time_s=self.dwell_time_s)
            self.finished.emit()


    def __init__(self,window,
                  photon_counter:PhotonCounter,
                  running_config:config = config(),
                  image_scan_widget=None,
                    *args, **kwargs):
        
        super().__init__(*args, **kwargs)

        # Setting device controls 
        self.photon_counter = photon_counter
        self.image_scan_widget = image_scan_widget

        self.running_config = running_config
        self.dpi = running_config.graph_dpi

        # Adding form to window
        self.setupUi(window)
        self._running = False

        # # Setting Scan Range to Default Maximum of Z Scanner
        self.running_counts_dwell_time_spin_box.setValue(self.running_config.dwell_time_ms)
        self.running_counts_number_of_points.setValue(self.running_config.number_of_points)
        self.running_counts_delay_spin_box.setValue(self.running_config.refresh_time_ms*1e-3)

        
        # Connecting Buttons 
        # self.z_scan_start_button.clicked.connect(self.start_z_scan)
        # self.show_peaks_push_button.clicked.connect(self.show_peaks)
        self.running_counts_delay_spin_box.valueChanged.connect(self.update_timer_interval)
        self.running_counts_number_of_points.valueChanged.connect(self.update_array_lengths)
        self.running_counts_dwell_time_spin_box.valueChanged.connect(self.update_timer_interval)
        self.running_counts_push_button.clicked.connect(self.update_button)
        self.running_counts_push_button.setCheckable(True)
        self.reset_running_counts_push_button.clicked.connect(self.reset_graph)

        # Preallocation arrays 
        self._time_s = np.zeros(self.running_config.number_of_points)
        self._kcounts_per_second = np.zeros(self.running_config.number_of_points)
        self._start_time = time.time()


        ## Graphing 
        self.z_scan_data = None

        # Getting frame size
        frame_size = self.running_counts_plot_frame.frameSize()
        px_x = frame_size.width()
        px_y = frame_size.height()
   
        # Creating the image scan plot and the toolbar
        self.canvas = FigureCanvasQTAgg(plt.Figure(figsize=(px_x/self.dpi,px_y/self.dpi), dpi=self.dpi))
        self.toolbar = NavigationToolbar(self.canvas,self.running_counts_toolbar_frame)
        self.toolbar.setFixedWidth(px_x)
        self.canvas.setParent(self.running_counts_plot_frame)
        self.insert_ax()

        # Creating updating timer 
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(self.running_config.refresh_time_ms)


    def update_timer_interval(self):
        self.timer.setInterval(int(self.running_counts_delay_spin_box.value()*1e3))

    def update_array_lengths(self):
        new_number = int(self.running_counts_number_of_points.value())
        
        # If the new number is larger we want to extend the arrays 
        if (current_number := len(self._time_s)) < new_number:
            self._time_s = np.append(self._time_s, np.zeros(int(new_number-current_number)))
            self._kcounts_per_second = np.append(self._kcounts_per_second, np.zeros(int(new_number-current_number)))
        # If it is smaller we want to shrink the arrays 
        else:
            self._time_s = self._time_s[-new_number:]
            self._kcounts_per_second = self._kcounts_per_second[-new_number:]

    def insert_ax(self):

        font = {
            'weight': 'normal',
            'size': 3
        }
        matplotlib.rc('font', **font)
       
        self.ax = self.canvas.figure.subplots()     
        self.ax.tick_params(axis='both', which='major', labelsize=3, width=.5, length=2, tick1On=True, tick2On=False, pad=0)
        
        for axis in 'left', 'bottom','top','right':
            self.ax.spines[axis].set_linewidth(.5)
   
     
        self.running_counts_plot = self.ax.plot([],[], c=self.running_config.line_color)[0]

        self.ax.set_xlabel("Time(s)", loc='right',labelpad=0)
        self.ax.set_ylabel("kCounts/s", loc='top',labelpad=0)

        self.canvas.figure.patch.set_facecolor('None')

        self.canvas.draw()
        self.canvas.figure.tight_layout()


    def update_running_counts_graph(self):

        if self.running_counts_plot:
            self.running_counts_plot.remove()

        times = self._time_s[self._time_s != 0]
        k_counts = self._kcounts_per_second[self._time_s != 0]
            
        self.running_counts_plot = self.ax.plot(times,
                                        k_counts,
                                        c=self.running_config.line_color,
                                        linewidth=0.5)[0]
        
        # Updating the limits of the axis 
        if len(times)>0:
            if (time_min := min(times)) != (time_max := max(times)):
                self.ax.set_xlim([time_min,time_max])

            if (k_min := min(k_counts)) != (k_max := max(k_counts)):
                self.ax.set_ylim([k_min*0.99,k_max*1.01])
            else:
                "set auto"

        self.canvas.figure.tight_layout()
        self.canvas.draw()

        
    def scanning_thread(self):

        def update_after_scan():
            # adding new image to the ui
            k_counts_per_sec = int(self.worker.counts/1000)
            array_length = len(self._kcounts_per_second)
            
            # Adding to the array 
            self._kcounts_per_second = np.roll(self._kcounts_per_second, -1) 
            self._kcounts_per_second[array_length-1] = k_counts_per_sec 
            self._time_s = np.roll(self._time_s, -1) 
            self._time_s[array_length-1] = time.time()-self._start_time 
            

        # Getting spin box values 
        dwell_time_s = self.running_counts_dwell_time_spin_box.value()*1e-3

        # Starting asynchronous thread
        self.thread = QThread()
        self.worker = RunningCountsWidget.Worker(dwell_time_s=dwell_time_s,
                                                 photon_counter=self.photon_counter)

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

        # Locking the buttons so you can't start a new scan 
        self.thread.finished.connect(update_after_scan)

        self.thread
    
    def reset_graph(self):
        self._kcounts_per_second[:] = 0
        self._time_s[:] = 0
        self.update_running_counts_graph()

    def update_button(self):
        if self.running_counts_push_button.isChecked():
            self._running = True
            self.running_counts_push_button.setText("Stop Running")
        else:
            self._running = False
            self.running_counts_push_button.setText("Start Running")

    def update_ui(self):
        if self.running_counts_push_button.isChecked():
            # Getting the counts per second  
            self.scanning_thread()
            self.update_running_counts_graph()

    def freeze_gui(self):
        """This is a function that is called to freeze the GUI when another program is running 
        """
        self.running_counts_push_button.setEnabled(False)
        self.running_counts_delay_spin_box.setEnabled(False)

        if self.image_scan_widget != None:
            self.image_scan_widget.x_confocal_spin_box.setEnabled(True)
            self.image_scan_widget.y_confocal_spin_box.setEnabled(True)
            self.image_scan_widget.z_confocal_spin_box.setEnabled(True)

    
    def unfreeze_gui(self): 
        """Returns control to all commands for the GUI after the programs have finished running 
        """
        self.running_counts_push_button.setEnabled(True)
        self.running_counts_delay_spin_box.setEnabled(True)


if __name__ == "__main__":
    from experimental_configuration import *
    from PyQt5.QtWidgets import QApplication,QMainWindow

    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = RunningCountsWidget(window,photon_counter=photon_counter_1,default_save_config="")
    window.show()
    app.exec()

