#############################################################################################
# Third party
import sys
import numpy as np
from dataclasses import dataclass
import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.axes_grid1 import make_axes_locatable
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

# Classes for Typing
from NV_ABJ.experimental_logic.confocal_scanning import ConfocalControls
# Importing generated python code from qtpy ui
from NV_ABJ.user_interfaces.tracking_widget.generated_ui import Ui_TrackingWidget
#############################################################################################


# Making a class that inherits the python base code produced by the user interface
class TrackingWidget(Ui_TrackingWidget):
    # Asynchronous running of the confocal scanning 
    @dataclass
    class PlotConfig:
        cmap:str = "pink"
        position_marker_color:str = "blue"
        z_scan_color:str = "blue"
        z_scan_position_line_color:str = "grey"
        dpi:int = 300
        
    class Worker(QObject):
        finished = pyqtSignal()
        progress = pyqtSignal(int)

        def __init__(self,x_position:float,
                        y_position:float,
                        z_position:float,
                        confocal_controls:ConfocalControls,
                        *args,**kwargs):
            
            super().__init__(*args,**kwargs)
            self.x_position = x_position
            self.y_position = y_position
            self.z_position = z_position
            self.confocal_controls = confocal_controls
            self.new_x = None
            self.new_y = None
            self.new_z = None
            self.tracking_graphs = None

        def run(self):
            self.new_x,self.new_y,self.new_z,self.tracking_graphs = self.confocal_controls.tracking(x_position=self.x_position,
                                                    y_position=self.y_position,
                                                    z_position=self.z_position)
            self.finished.emit()

    def __init__(self,window,
                 confocal_controls:ConfocalControls,
                  config:PlotConfig = PlotConfig(),
                    *args, **kwargs):
        
        super().__init__(*args, **kwargs)

        # Setting device controls 
        self.window = window
        self.confocal_controls = confocal_controls
        self.config = config
        self.dpi = config.dpi
        self.default_cmap = config.cmap

        # Adding form to window
        self.setupUi(self.window)

        # Connecting buttons 
        self.start_tracking_push_button.clicked.connect(self.tracking_thread)

        # Creating tracking images 
       # Getting frame size
        image_frame_size = self.tracking_image_frame.frameSize()
        image_scan_px_x = image_frame_size.width()
        image_scan_px_y = image_frame_size.height()
   
        z_frame_size = self.tracking_z_frame.frameSize()
        z_frame_size_px_x = z_frame_size.width()
        z_frame_size_px_y = z_frame_size.height()

        # Creating the image scan plot and the toolbar 
        self.tracking_image_canvas = FigureCanvasQTAgg(plt.Figure(figsize=(image_scan_px_x/self.dpi,image_scan_px_y/self.dpi), dpi=self.dpi))
        self.tracking_z_scan_canvas = FigureCanvasQTAgg(plt.Figure(figsize=(z_frame_size_px_x/self.dpi,z_frame_size_px_y/self.dpi), dpi=self.dpi))
        self.tracking_image_canvas.setParent(self.tracking_image_frame)
        self.tracking_z_scan_canvas.setParent(self.tracking_z_frame)

        # Updating tracking ui to match settings of the confocal class initially 
        self.dwell_time_ms_spin_box_tracking.setValue(self.confocal_controls.tracking_dwell_time_s*1e3)
        self.z_span_spin_box_tracking.setValue(self.confocal_controls.tracking_z_span*1e6)
        self.xy_span_spin_box_tracking.setValue(self.confocal_controls.tracking_xy_span*1e6)
        self.z_points_spin_box_tracking.setValue(self.confocal_controls.tracking_z_number_of_points)
        self.xy_points_spin_box_tracking.setValue(self.confocal_controls.tracking_xy_number_of_points)

        self.insert_ax()
       
    def insert_ax(self):
        min_x = 0
        max_x = self.confocal_controls.tracking_xy_span
        min_y = 0
        max_y = self.confocal_controls.tracking_xy_span
        min_z =  0
        max_z = self.confocal_controls.tracking_z_span
    

        font = {
            'weight': 'normal',
            'size': 3
        }
        matplotlib.rc('font', **font)
       
        self.image_ax = self.tracking_image_canvas.figure.subplots()     
        self.image_ax.tick_params(axis='both', which='major', labelsize=3, width=.5, length=2, tick1On=True, tick2On=False, pad=0)
        
        for axis in 'left', 'bottom','top','right':
            self.image_ax.spines[axis].set_linewidth(.5)
   
     
        self.tracking_image_scan_plot = None
        self.tracking_image_scan_plot_colorbar = None
        self.tracking_image_position = None

        self.tracking_image_scan_plot = self.image_ax.imshow(np.zeros((self.confocal_controls.tracking_xy_number_of_points,self.confocal_controls.tracking_xy_number_of_points)),
                                                        cmap=self.default_cmap, interpolation='nearest',extent=[min_x*1e6,max_x*1e6,min_y*1e6,max_y*1e6], vmin=0.1)

        self.image_ax.set_xlabel("X(\u03bcm)", loc='right',labelpad=0)
        self.image_ax.set_ylabel("Y(\u03bcm)", loc='top',labelpad=0)

        self.tracking_image_canvas.figure.patch.set_facecolor('None')

        divider = make_axes_locatable(self.image_ax)
        self.cax = divider.append_axes("right", size="5%", pad=0.05)
        self.cax.tick_params(axis='both', which='major', labelsize=3, width=.5, length=2, tick1On=True, tick2On=False, pad=0)

        self.image_scan_plot_colorbar = self.tracking_image_canvas.figure.colorbar(self.tracking_image_scan_plot, cax=self.cax)
        self.cax.set_ylabel("kCounts/s")
        self.image_scan_plot_colorbar.outline.set_linewidth(.5)


        self.tracking_image_canvas.draw()
        self.tracking_image_canvas.figure.tight_layout()

        self.tracking_z_scan_plot = None
        self.tracking_z_pos = None

        self.z_scan_ax = self.tracking_z_scan_canvas.figure.subplots()     
        self.z_scan_ax.tick_params(axis='both', which='major', labelsize=3, width=.5, length=2, tick1On=True, tick2On=False, pad=0)
        
        for axis in 'left', 'bottom','top','right':
            self.z_scan_ax.spines[axis].set_linewidth(.5)
   
     
        self.z_scan_plot = None
        self.tracking_z_pos = None

        self.tracking_z_scan_plot = self.z_scan_ax.plot(np.zeros(self.confocal_controls.tracking_xy_number_of_points),np.zeros(self.confocal_controls.tracking_xy_number_of_points),
                                                        c=self.config.z_scan_color)[0]
        self.tracking_z_pos = self.z_scan_ax.axvline(0*1e6,linestyle="--",c=self.config.z_scan_position_line_color)

        self.z_scan_ax.set_xlim([min_z*1e6,max_z*1e6])
        self.z_scan_ax.set_xlabel("X(\u03bcm)", loc='right',labelpad=0)
        self.z_scan_ax.set_ylabel("kCounts/s", loc='top',labelpad=0)

        self.tracking_z_scan_canvas.figure.patch.set_facecolor('None')

    # Scanning 
    def update_tracking_graphs(self,tracking_graphs:tuple,x_pos:float,y_pos:float,z_pos:float):
        xy_2d_scan = tracking_graphs[0]
        z_1d_scan = tracking_graphs[1]
        x_positions = tracking_graphs[2]
        y_positions = tracking_graphs[3]
        z_positions = tracking_graphs[4]

        if self.tracking_image_scan_plot:
            self.tracking_image_scan_plot.remove()

        if self.tracking_image_position:
            self.tracking_image_position.remove()


        xy_counts_image_scan = xy_2d_scan/1000    

        self.tracking_image_scan_plot = self.image_ax.imshow(xy_counts_image_scan, cmap=self.default_cmap, interpolation='nearest',
                                              extent=[min(x_positions)*1e6,max(x_positions)*1e6,min(y_positions)*1e6,max(y_positions)*1e6], vmin=0.1)
        self.tracking_image_position = self.image_ax.scatter(x_pos*1e6,y_pos*1e6,color=self.config.position_marker_color,s=2)
        
        self.tracking_image_scan_plot.set_extent([min(x_positions)*1e6,max(x_positions)*1e6,min(y_positions)*1e6,max(y_positions)*1e6])
        self.tracking_image_scan_plot.set_clim(np.min(xy_counts_image_scan),np.max(xy_counts_image_scan))

        self.image_scan_plot_colorbar.update_normal(self.tracking_image_scan_plot)
        self.tracking_image_canvas.figure.tight_layout()
        self.tracking_image_canvas.draw()


        
        if self.tracking_z_scan_plot:
            self.tracking_z_scan_plot.remove()

        if self.tracking_z_pos:
            self.tracking_z_pos.remove()

        self.tracking_z_scan_plot = self.z_scan_ax.plot(z_positions*1e6,z_1d_scan/1000, c=self.config.z_scan_color)[0]
        self.tracking_z_pos = self.z_scan_ax.axvline(z_pos*1e6,linestyle="--",c=self.config.z_scan_position_line_color)
        self.z_scan_ax.set_xlim([min(z_positions)*1e6,max(z_positions)*1e6])
        self.z_scan_ax.set_ylim([min(z_1d_scan)*1e-3,max(z_1d_scan)*1e-3])

        print(z_pos)

        self.tracking_z_scan_canvas.figure.tight_layout()
        self.tracking_z_scan_canvas.draw()
    

    def tracking_thread(self):

        def update_after_scan():
            # adding new image to the ui
            self.update_tracking_graphs(self.worker.tracking_graphs,self.worker.new_x,self.worker.new_y,self.worker.new_z)
            self.start_tracking_push_button.setEnabled(True)

        # Getting spin box values 
        dwell_time_s = self.dwell_time_ms_spin_box_tracking.value()*1e-3
        self.confocal_controls.tracking_dwell_time_s = dwell_time_s
        self.confocal_controls.tracking_xy_number_of_points = self.xy_points_spin_box_tracking.value()
        self.confocal_controls.tracking_z_number_of_points = self.z_points_spin_box_tracking.value()
        self.confocal_controls.tracking_xy_span = self.xy_span_spin_box_tracking.value()*1e-6
        self.confocal_controls.tracking_z_span = self.z_span_spin_box_tracking.value()*1e-6

        # Starting asynchronous thread
        self.thread = QThread()
        self.worker = TrackingWidget.Worker(x_position=self.confocal_controls.get_position_m()[0],
                             y_position=self.confocal_controls.get_position_m()[1],
                             z_position=self.confocal_controls.get_position_m()[2],
                             confocal_controls=self.confocal_controls)

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

        # Locking the buttons so you can't start a new scan 
        self.start_tracking_push_button.setEnabled(False)
        # Unlocking the buttons 
        self.thread.finished.connect(update_after_scan)

        self.thread

if __name__ == "__main__":
    from experimental_configuration.experimental_logic import *

    app = QtWidgets.QApplication(sys.argv)

    main_window = QtWidgets.QMainWindow()
    ui = TrackingWidget(main_window,confocal_controls=confocal_controls)

    main_window.show()
    app.exec()