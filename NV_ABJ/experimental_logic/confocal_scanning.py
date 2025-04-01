__all__ = ["ConfocalScanningDisplay","ConfocalScanningControls"]
from NV_ABJ import ScannerSingleAxis,PhotonCounter,meters

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
import matplotlib.font_manager as fm

import numpy as np
from numpy.typing import NDArray

class ConfocalScanningDisplay:
    """A grouping of functions that are used to quickly plot outputs for the confocal images 
    """
    
    def plot_image_scan(image_data,x_positions_m,y_positions_m,length_units:meters=meters.m,include_scale_bar=False,include_axis=True,bar_size:int = 10e-6):
        x_positions_m = x_positions_m/length_units.value
        y_positions_m = y_positions_m/length_units.value
        bar_size = bar_size

        fig, ax = plt.subplots()
        ax.imshow(image_data,extent=[x_positions_m[0],x_positions_m[1],y_positions_m[0],y_positions_m[1]]) 

        if include_scale_bar:
            fontprops = fm.FontProperties(size=18)

            scalebar = AnchoredSizeBar(ax.transData,
                                    bar_size, f'{bar_size} {length_units.name}', 'lower center', 
                                    pad=0.1,
                                    color='white',
                                    frameon=False,
                                    size_vertical=5,
                                    fontproperties=fontprops)

            ax.add_artist(scalebar)
        
        if not include_axis:
            ax.axis(False)

        return fig



class ConfocalScanningControls:

    def __init__(self,positioner_x:ScannerSingleAxis,positioner_y:ScannerSingleAxis,positioner_z:ScannerSingleAxis,photon_counter:PhotonCounter):
        self.positioner_x = positioner_x
        self.positioner_y = positioner_y
        self.positioner_z = positioner_z
        self.photon_counter = photon_counter
    
    def two_dimensional_scanning_raw(self,positions_x_m:tuple,positions_y_m:tuple,dwell_time_s:float,resolution:int)-> tuple[NDArray[np.int64],NDArray[np.float64],NDArray[np.float64]]:
        """This creates a two dimensional array over a selected region to scan 

        Args:
            positions_x_m (tuple): Scanning ranges for x 
            positions_y_m (tuple): Scanning ranges for y
            dwell_time_s (float): How long we will dwell at each point
            resolution (int): How many points per axis will be taken 

        Returns:
            tuple[NDArray[np.int64],NDArray[np.float64],NDArray[np.float64]]: (counts,x_positions,y_positions) Returns the counts for the photons along with the nominal x and y positions of the points 
        """
        # Make positions space
        x_positions = np.linspace(positions_x_m[0],positions_x_m[1],resolution)
        y_positions = np.linspace(positions_y_m[0],positions_y_m[1],resolution)

        # Preallocate memory 
        photon_count_image = np.zeros((resolution,resolution))

        # Iterate through all positions 
        for ind_y,y in enumerate(y_positions):
            for ind_x,x in enumerate(x_positions):
                self.positioner_x.set_position_m(x)
                self.positioner_y.set_position_m(y)

                # Get photon counts and return the matrix 
                photon_count = self.photon_counter.get_counts_raw(dwell_time_s)
                photon_count_image[ind_x,ind_y] = photon_count
        
        return photon_count_image,x_positions,y_positions
    
    def two_dimensional_scanning_per_second(self,positions_x_m:tuple,positions_y_m:tuple,dwell_time_s:float,resolution:int)-> tuple[NDArray[np.int64],NDArray[np.float64],NDArray[np.float64]]:
        counts,x,y  = self.two_dimensional_scanning_raw(positions_x_m,positions_y_m,dwell_time_s,resolution)
        counts_per_second = np.round(counts/dwell_time_s)
        return counts_per_second,x,y

    def z_scan_raw(self,z_positions_m:tuple,dwell_time_s:float,resolution:int)->tuple[NDArray[np.int64],NDArray[np.float64]]:
        """Scans at a single x and y position and scans in z

        Args:
            z_positions_m (tuple): (z minimum, z maximum)
            dwell_time_s (float): time for taking data before moving to next point
            resolution (int): how many points of data will be taken 

        Returns:
            tuple[NDArray[np.int64],NDArray[np.float64]]: _description_
        """
        z_positions = np.linspace(z_positions_m[0],z_positions_m[1],resolution)
        photon_counts = np.zeros(resolution)

        for ind,z in enumerate(z_positions):
            self.positioner_z.set_position_m(z)
            photon_count = self.photon_counter.get_counts_raw(dwell_time_s)
            photon_counts[ind] = photon_count
        
        return photon_counts, z_positions

    def z_scan_per_second(self,z_positions_m:tuple,dwell_time_s:float,resolution:int)->tuple[NDArray[np.int64],NDArray[np.float64]]:
        counts, z = self.z_scan_raw(z_positions_m,dwell_time_s,resolution)
        counts_per_second = np.round(counts/dwell_time_s)
        return counts_per_second,z

    def tracking_on_point(self):
        ...