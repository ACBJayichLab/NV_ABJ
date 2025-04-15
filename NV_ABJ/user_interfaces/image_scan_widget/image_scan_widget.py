#############################################################################################
# Third party
import sys
import numpy as np
from dataclasses import dataclass
import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.axes_grid1 import make_axes_locatable
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar

# Classes for Typing
from NV_ABJ.experimental_logic.confocal_scanning import ConfocalControls

# Importing generated python code from qtpy ui
from generated_ui import Ui_ImageScanWidget
#############################################################################################

# Making a class that inherits the python base code produced by the user interface
class ImageScanWidget(Ui_ImageScanWidget):
    @dataclass
    class ImageScanWidgetConfig:
        cmap:str = "pink"
        cursor_color:str = "g"
        cursor_shape:str = "o"
        graph_dpi:int = 300

    # Asynchronous running of the confocal scanning 
    class Worker(QObject):
        finished = pyqtSignal()
        progress = pyqtSignal(int)

        def __init__(self,dwell_time_s:float,
                        x_positions:float,
                        y_positions:float,
                        z_position:float,
                        confocal_controls:ConfocalControls,
                        *args,**kwargs):
            
            super().__init__(*args,**kwargs)
            self.dwell_time_s = dwell_time_s
            self.x_positions = x_positions
            self.y_positions = y_positions
            self.z_position = z_position
            self.confocal_controls = confocal_controls
            self.xy_scan = None

        def run(self):
            self.xy_scan = confocal_controls.xy_scan(dwell_time_s=self.dwell_time_s ,
                                                                x_positions=self.x_positions,
                                                                y_positions=self.y_positions,
                                                                z_position=self.z_position)
            self.finished.emit()


    def __init__(self,window,
                  confocal_controls:ConfocalControls,
                  default_save_config,
                  image_scan_config:ImageScanWidgetConfig = ImageScanWidgetConfig(),
                    *args, **kwargs):
        
        super().__init__(*args, **kwargs)

        # Setting device controls 
        self.window = window
        self.confocal_controls = confocal_controls
        self.default_save_config = default_save_config
            
        self.confocal_controls.set_position_m(*self.default_position_um)

        self.image_scan_config = image_scan_config

        self.default_cmap = image_scan_config.cmap
        self.dpi = image_scan_config.graph_dpi

        # Adding form to window
        self.setupUi(self.window)

        # Setting the cursor updating to false by default
        self._cursor_update_location = False

        # Setting the default position 
        self.x_confocal_spin_box.setValue(self.default_position_um[0])
        self.y_confocal_spin_box.setValue(self.default_position_um[1])
        self.z_confocal_spin_box.setValue(self.default_position_um[2])


        # Getting frame size
        image_frame_size = self.image_scan_frame.frameSize()
        image_scan_px_x = image_frame_size.width()
        image_scan_px_y = image_frame_size.height()
   
        # Creating the image scan plot and the toolbar 
        self.canvas = FigureCanvasQTAgg(plt.Figure(figsize=(image_scan_px_x/self.dpi,image_scan_px_y/self.dpi), dpi=self.dpi))
        self.toolbar = NavigationToolbar(self.canvas,self.toolbar_frame_image_scan)
        self.toolbar.setFixedWidth(image_scan_px_x)
        self.canvas.setParent(self.image_scan_frame)
        self.insert_ax()
       
        # Connecting Scanner Buttons
        self.full_image_scan_push_button.clicked.connect(self.full_image_scan)
        self.local_image_scan_push_button.clicked.connect(self.local_image_scan)
        self.update_cursor_location_push_button.clicked.connect(self.cursor_update_location)
        self.show_cursor_radio_button.toggled.connect(self.update_cursor)


        # Connecting spin boxes to update the confocal position when changed 
        self.x_confocal_spin_box.valueChanged.connect(self.update_confocal_position)
        self.y_confocal_spin_box.valueChanged.connect(self.update_confocal_position)
        self.z_confocal_spin_box.valueChanged.connect(self.update_confocal_position)
        

    # Easy calls for the position limits 
    @property
    def x_scanning_range(self) -> tuple[float,float]:
        return self.confocal_controls.scanner_x.position_limits_m
    
    @property
    def y_scanning_range(self) -> tuple[float,float]:
        return self.confocal_controls.scanner_y.position_limits_m
   
    @property
    def z_scanning_range(self) -> tuple[float,float]:
        return self.confocal_controls.scanner_z.position_limits_m
    
    def update_on_graph_resize(self, *args, **kwargs):
        self.canvas.figure.tight_layout()

    def update_cursor(self):

        if self.cursor_plot:
            self.cursor_plot.remove()
        
        if self.show_cursor_radio_button.isChecked():
            self.cursor_plot = self.ax.scatter(self.confocal_controls.get_position_m()[0]*1e-6,
                                               self.confocal_controls.get_position_m()[1]*1e-6,
                                                 marker=self.image_scan_config.cursor_shape,
                                               linewidths=0.5, s=20, facecolors='none', color=self.image_scan_config.cursor_color)
        else:
            self.cursor_plot = self.ax.scatter(self.confocal_controls.get_position_m()[0]*1e-6,
                                               self.confocal_controls.get_position_m()[1]*1e-6,
                                                marker=self.image_scan_config.cursor_shape,
                                               linewidths=0.5, s=20, facecolors='none', color='None')
        self.canvas.draw()
        

    def onclick(self,event):

        # This is allowing us to update the location of the cursor if there is not a task running 
        if self._cursor_update_location:
            x_pos = event.xdata
            y_pos = event.ydata
            if x_pos != None and y_pos != None:
                self._cursor_update_location = False    

                self.x_confocal_spin_box.setValue(x_pos)
                self.y_confocal_spin_box.setValue(y_pos)
                self._cursor_update_location = False    

                self.update_confocal_position()




    def cursor_update_location(self):
        self._cursor_update_location = True 

    def insert_ax(self):
        min_x = self.x_scanning_range[0]
        max_x = self.x_scanning_range[1]
        min_y = self.y_scanning_range[0]
        max_y = self.y_scanning_range[1]
    

        font = {
            'weight': 'normal',
            'size': 3
        }
        matplotlib.rc('font', **font)
       
        self.ax = self.canvas.figure.subplots()     
        self.ax.tick_params(axis='both', which='major', labelsize=3, width=.5, length=2, tick1On=True, tick2On=False, pad=0)
        
        for axis in 'left', 'bottom','top','right':
            self.ax.spines[axis].set_linewidth(.5)
   
     
        self.cursor_plot = None
        self.image_scan_plot = None
        self.image_scan_plot_colorbar = None

        self.image_scan_plot = self.ax.imshow(np.zeros((50,50)), cmap=self.default_cmap, interpolation='nearest',extent=[min_x*1e6,max_x*1e6,min_y*1e6,max_y*1e6], vmin=0.1)

        self.ax.set_xlabel("X(\u03bcm)", loc='right',labelpad=0)
        self.ax.set_ylabel("Y(\u03bcm)", loc='top',labelpad=0)

        self.canvas.figure.patch.set_facecolor('None')

        divider = make_axes_locatable(self.ax)
        self.cax = divider.append_axes("right", size="5%", pad=0.05)
        self.cax.tick_params(axis='both', which='major', labelsize=3, width=.5, length=2, tick1On=True, tick2On=False, pad=0)

        self.image_scan_plot_colorbar = self.canvas.figure.colorbar(self.image_scan_plot, cax=self.cax)
        self.cax.set_ylabel("kCounts/s")
        self.image_scan_plot_colorbar.outline.set_linewidth(.5)


        self.canvas.mpl_connect('button_release_event',self.onclick)
        self.ax.callbacks.connect('xlim_changed', self.update_on_graph_resize)
        self.ax.callbacks.connect('ylim_changed', self.update_on_graph_resize)


        self.canvas.draw()
        self.canvas.figure.tight_layout()

    # Scanning 
    def update_image_scan(self,xy_scan):

        if self.image_scan_plot:
            self.image_scan_plot.remove()


        xy_counts_image_scan = xy_scan[0]/1000
        x_positions = xy_scan[1]
        y_positions = xy_scan[2]
    

        self.image_scan_plot = self.ax.imshow(xy_counts_image_scan, cmap=self.default_cmap, interpolation='nearest',
                                              extent=[min(x_positions)*1e6,max(x_positions)*1e6,min(y_positions)*1e6,max(y_positions)*1e6], vmin=0.1)
        
        self.ax.set_xbound([min(x_positions)*1e6,max(x_positions)*1e6])
        self.ax.set_ybound([min(y_positions)*1e6,max(y_positions)*1e6])
        self.image_scan_plot.set_extent([min(x_positions)*1e6,max(x_positions)*1e6,min(y_positions)*1e6,max(y_positions)*1e6])
        self.image_scan_plot.set_clim(np.min(xy_counts_image_scan),np.max(xy_counts_image_scan))

        self.image_scan_plot_colorbar.update_normal(self.image_scan_plot)
        self.canvas.figure.tight_layout()

        # Updates the toolbar area 
        self.toolbar.update()

        self.canvas.draw()

    def scanning_thread(self,x_positions,y_positions):

        def update_after_scan():
            # adding new image to the ui
            self.update_image_scan(self.worker.xy_scan)
            self.full_image_scan_push_button.setEnabled(True)
            self.local_image_scan_push_button.setEnabled(True)

        # Getting spin box values 
        z_position = self.z_position
        dwell_time_s = self.dwell_time_image_scan_spin_box.value()*1e-3

        # Starting asynchronous thread
        self.thread = QThread()
        self.worker = ImageScanWidget.Worker(dwell_time_s=dwell_time_s,
                             x_positions=x_positions,
                             y_positions=y_positions,
                             z_position=z_position,
                             confocal_controls=self.confocal_controls)

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

        # Locking the buttons so you can't start a new scan 
        self.full_image_scan_push_button.setEnabled(False)
        self.local_image_scan_push_button.setEnabled(False)
        # Unlocking the buttons 
        self.thread.finished.connect(update_after_scan)

        self.thread

    def full_image_scan(self):
        min_x = self.x_scanning_range[0]
        max_x = self.x_scanning_range[1]
        min_y = self.y_scanning_range[0]
        max_y = self.y_scanning_range[1]
    

        x_positions = np.linspace(min_x,max_x,self.image_scan_resolution_spin_box.value())
        y_positions = np.linspace(min_y,max_y,self.image_scan_resolution_spin_box.value())

        self.scanning_thread(x_positions=x_positions,y_positions=y_positions)

    def local_image_scan(self):
        x_bounds = self.ax.get_xbound()
        y_bounds = self.ax.get_ybound()

        x_positions = np.linspace(x_bounds[0]*1e-6,x_bounds[1]*1e-6,self.image_scan_resolution_spin_box.value())
        y_positions = np.linspace(y_bounds[0]*1e-6,y_bounds[1]*1e-6,self.image_scan_resolution_spin_box.value())

        self.scanning_thread(x_positions=x_positions,y_positions=y_positions)


    # Adjusting the confocal based on spin boxes  
    def update_confocal_position(self):
        confocal_controls.set_position_m(self.x_position,self.y_position,self.z_position )
        self.update_cursor()
    
    
if __name__ == "__main__":
    # Hardware and logic imports
    from experimental_configuration.experimental_logic import confocal_controls

    app = QtWidgets.QApplication(sys.argv)
    MainWindow =QtWidgets.QMainWindow()
    # MainWindow.setFixedSize(730, 410)

    ui = ImageScanWidget(MainWindow,
                         confocal_controls=confocal_controls,
                         default_save_config=None)
    

    MainWindow.show()
    app.exec()
