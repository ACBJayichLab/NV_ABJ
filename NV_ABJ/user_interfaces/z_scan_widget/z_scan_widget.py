#############################################################################################
# Third party
import sys
import numpy as np
from dataclasses import dataclass
import matplotlib.pyplot as plt
import matplotlib
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from scipy.signal import find_peaks
# Classes for Typing
from NV_ABJ.experimental_logic.confocal_scanning import ConfocalControls

# Importing generated python code from qtpy ui
from NV_ABJ.user_interfaces.z_scan_widget.generated_ui import Ui_z_scan_widget
#############################################################################################

class ZScanWidget(Ui_z_scan_widget):
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
        default_peak_distance:int = 50


    # Asynchronous running of the confocal scanning 
    class Worker(QObject):
        finished = pyqtSignal()
        progress = pyqtSignal(int)

        def __init__(self,dwell_time_s:float,
                        x_position:float,
                        y_position:float,
                        z_positions:float,
                        confocal_controls:ConfocalControls,
                        *args,**kwargs):
            
            super().__init__(*args,**kwargs)
            self.dwell_time_s = dwell_time_s
            self.x_position = x_position
            self.y_position = y_position
            self.z_positions = z_positions
            self.confocal_controls = confocal_controls
            self.z_scan_counts = None

        def run(self):
            self.z_scan_counts,_ = self.confocal_controls.z_scan(dwell_time_s=self.dwell_time_s ,
                                                                x_position=self.x_position,
                                                                y_position=self.y_position,
                                                                z_positions=self.z_positions)
            self.finished.emit()


    def __init__(self,window,
                  confocal_controls:ConfocalControls,
                  default_save_config,
                  z_scan_config:config = config(),
                    *args, **kwargs):
        
        super().__init__(*args, **kwargs)

        # Setting device controls 
        self.confocal_controls = confocal_controls
        self.default_save_config = default_save_config

        self.z_scan_config = z_scan_config
        self.dpi = z_scan_config.graph_dpi

        # Adding form to window
        self.setupUi(window)

        # Setting Scan Range to Default Maximum of Z Scanner
        self.z_limits =  self.confocal_controls.scanner_z.position_limits_m
        self.z_scan_minimum_spin_box.setValue(self.z_limits[0]*1e6)
        self.z_scan_maximum_spin_box.setValue(self.z_limits[1]*1e6)
        self.z_scan_dwell_time_image_scan_spin_box.setValue(self.z_scan_config.dwell_time_ms)
        self.z_scan_number_of_points_spin_box.setValue(self.z_scan_config.number_of_points)
        self.peak_distance_spin_box.setValue(self.z_scan_config.default_peak_distance)
        
        # Connecting Buttons 
        self.z_scan_start_button.clicked.connect(self.start_z_scan)
        self.show_peaks_push_button.clicked.connect(self.show_peaks)
        self.peak_distance_spin_box.valueChanged.connect(self.show_peaks)


        ## Graphing 
        self.z_scan_data = None

        # Getting frame size
        z_plot_frame_size = self.z_scan_plot_frame.frameSize()
        z_scan_px_x = z_plot_frame_size.width()
        z_scan_px_y = z_plot_frame_size.height()
   
        # Creating the image scan plot and the toolbar
        self.canvas = FigureCanvasQTAgg(plt.Figure(figsize=(z_scan_px_x/self.dpi,z_scan_px_y/self.dpi), dpi=self.dpi))
        self.toolbar = NavigationToolbar(self.canvas,self.z_scan_toolbar_frame)
        self.toolbar.setFixedWidth(z_scan_px_x)
        self.canvas.setParent(self.z_scan_plot_frame)
        self.insert_ax()

        # This is so if we want to show peaks we can otherwise we wont
        self._z_positions = []
        self._z_counts = []



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
   
     
        self.z_scan_plot = self.ax.plot([],[], c=self.z_scan_config.line_color)[0]
        self.z_scan_peaks_plot = self.ax.scatter([],[], c=self.z_scan_config.line_color)
        self.z_scan_maximum_plot = self.ax.scatter([],[], c=self.z_scan_config.line_color)


        self.ax.set_xlabel("Z(\u03bcm)", loc='right',labelpad=0)
        self.ax.set_ylabel("kCounts/s", loc='top',labelpad=0)

        self.canvas.figure.patch.set_facecolor('None')

        self.canvas.draw()
        self.canvas.figure.tight_layout()

    def show_peaks(self):
        # Removing plots to repopulate if needed 
        if self.z_scan_peaks_plot:
            self.z_scan_peaks_plot.remove()
        if self.z_scan_maximum_plot:
            self.z_scan_maximum_plot.remove()

        # Finding absolute max for data
        if len(self._z_counts) > 0 and len(self._z_positions) > 0:
            # Finding absolute maximum              
            maximum_ind = np.argmax(self._z_counts)
            z_pos_max_um = self._z_positions[maximum_ind]*1e6
            z_kcount_per_s_max = self._z_counts[maximum_ind]/1000

            # Updating the max text for the peak position 
            self.z_max_position_label.setText(f"Z(μm): {z_pos_max_um:.3e}")
            self.z_counts_max_label.setText(f"kCounts/s: {z_kcount_per_s_max:.3e}")
        
        else:
            # Updating the max text for the peak position 
            self.z_max_position_label.setText(f"Z(μm):")
            self.z_counts_max_label.setText(f"kCounts/s:")
        
        # Adding peaks to graph or removing them as an empty scatter
        if self.show_peaks_push_button.isChecked() and len(self._z_counts) > 0 and len(self._z_positions) > 0:
        
            peaks, _ = find_peaks(self._z_counts,distance=self.peak_distance_spin_box.value())

            # Plotting peaks and maximum 
            self.z_scan_peaks_plot = self.ax.scatter(self._z_positions[peaks]*1e6,self._z_counts[peaks]/1000, c=self.z_scan_config.cursor_color,s=self.z_scan_config.cursor_size)
            self.z_scan_maximum_plot = self.ax.scatter(z_pos_max_um,z_kcount_per_s_max, c=self.z_scan_config.maximum_cursor_color,s=self.z_scan_config.cursor_max_size)



        else:
            # Adding blanks if there are no peaks 
            self.z_scan_peaks_plot = self.ax.scatter([],[], c=self.z_scan_config.line_color)
            self.z_scan_maximum_plot = self.ax.scatter([],[], c=self.z_scan_config.line_color)
                
        self.canvas.figure.tight_layout()
        self.canvas.draw()




    def update_z_scan(self,z_positions, z_scan_counts):

        if self.z_scan_plot:
            self.z_scan_plot.remove()

            
        self.z_scan_plot = self.ax.plot(z_positions*1e6,
                                        z_scan_counts/1000,
                                        c=self.z_scan_config.line_color,
                                        linewidth=0.5)[0]
        
        # Updating the limits of the axis 
        self.ax.set_xlim([min(z_positions)*1e6,max(z_positions)*1e6])
        self.ax.set_ylim([min(z_scan_counts)/1000*0.99,max(z_scan_counts)/1000*1.01])

        self.ax.set_xbound([min(z_positions)*1e6,max(z_positions)*1e6])
        self.ax.set_ybound([min(z_scan_counts)/1000*0.99,max(z_scan_counts)/1000*1.01])

        self.canvas.figure.tight_layout()
        self.canvas.draw()

        # Add peaks if needed 
        self.show_peaks()


        
    def scanning_thread(self,z_positions):

        def update_after_scan():
            # adding new image to the ui
            self._z_positions = z_positions
            self._z_counts = self.worker.z_scan_counts
            self.update_z_scan(z_positions=z_positions,z_scan_counts=self.worker.z_scan_counts)
            self.z_scan_start_button.setEnabled(True)

        # Getting spin box values 
        dwell_time_s = self.z_scan_dwell_time_image_scan_spin_box.value()*1e-3
        x_pos,y_pos,_ = self.confocal_controls.get_position_m()

        # Starting asynchronous thread
        self.thread = QThread()
        self.worker = ZScanWidget.Worker(dwell_time_s=dwell_time_s,
                                         x_position=x_pos,
                                         y_position=y_pos,
                                         z_positions=z_positions,
                                         confocal_controls=self.confocal_controls)

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

        # Locking the buttons so you can't start a new scan 
        self.z_scan_start_button.setEnabled(False)
        # Unlocking the buttons 
        self.thread.finished.connect(update_after_scan)

        self.thread

    def start_z_scan(self): 
        # Getting the z scan 
        z_positions = np.linspace(self.z_scan_minimum_spin_box.value()*1e-6,
                                  self.z_scan_maximum_spin_box.value()*1e-6,
                                  self.z_scan_number_of_points_spin_box.value())

        self.scanning_thread(z_positions=z_positions)





