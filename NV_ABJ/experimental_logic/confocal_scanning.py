__all__ = ["ConfocalControls"]

# basic Imports
import numpy as np
import matplotlib.pyplot as plt
from numpy.typing import NDArray
from NV_ABJ import ScannerSingleAxis, PhotonCounter

class ConfocalControls:
    def __init__(self,scanner_x:ScannerSingleAxis,scanner_y:ScannerSingleAxis,scanner_z:ScannerSingleAxis,photon_counter:PhotonCounter,
                 tracking_xy_span:float = 1.5e-6,tracking_z_span:float = 3e-6,tracking_dwell_time_s:float = 5e-3,tracking_xy_number_of_points:int = 10,tracking_z_number_of_points:int = 20):
        self.scanner_x = scanner_x
        self.scanner_y = scanner_y
        self.scanner_z = scanner_z
        self.photon_counter = photon_counter
        
        # Tracking parameters
        self.tracking_xy_span = tracking_xy_span
        self.tracking_z_span = tracking_z_span
        self.tracking_dwell_time_s = tracking_dwell_time_s
        self.tracking_xy_number_of_points = tracking_xy_number_of_points
        self.tracking_z_number_of_points = tracking_z_number_of_points


    def set_position_m(self,x_position:float,y_position:float,z_position:float)->None:
        """Sets the position of the confocal based on the inputs

        Args:
            x_position (float): position the x axis is going to be set to  
            y_position (float): position the y axis is going to be set to  
            z_position (float): position the z axis is going to be set to  
        """
        with self.scanner_x as x_con, self.scanner_y as y_con, self.scanner_z as z_con:
            x_con.set_position_m(x_position)
            y_con.set_position_m(y_position)
            z_con.set_position_m(z_position)

    def get_position_m(self)->tuple[float,float,float]:
        """This gets the position of the confocal position in meters 

        Returns:
            tuple[float,float,float]: (x,y,z)
        """
        with self.scanner_x as x_con, self.scanner_y as y_con, self.scanner_z as z_con:
            x_position = x_con.get_position_m()
            y_position = y_con.get_position_m()
            z_position = z_con.get_position_m()

        return x_position, y_position, z_position

    def xy_scan(self,dwell_time_s:float,x_positions:NDArray,y_positions:NDArray,z_position:float,*args,**kwargs)-> tuple[NDArray,NDArray,NDArray]:
        """An xy scan has the same z height for all points and translates to the x and y positions. This instance of the xy 
        scan iterates between scanning forward and backward so there is no sudden movement to the confocal. The arrays from 
        x and y when added will be sorted to ensure the locations are sequential. 

        Args:
            dwell_time_s (float): How long we dwell at each point before moving to the next point
            x_positions (NDArray): An array of the x_positions you want to scan over 
            y_positions (NDArray): An array of the y_positions you want to scan over 
            z_position (float): The z position we want to scan at

        Returns:
            NDArray: Photon counts. A 2D array of the photons per second at each point in the x y positions 
            NDArray: X positions. A sorted x array of the positions passed originally to the function 
            NDArray: Y positions. A sorted y array of the positions passed originally to the function
        """

        # Making sure the lists are ordered correctly 
        x_positions = sorted(x_positions)
        y_positions = sorted(y_positions)

        # Getting the basic length which is repeatedly used
        x_length = len(x_positions)

        # Pre allocating matrices
        xy_counts = np.zeros((x_length,len(y_positions)))
        line_counts = np.zeros(x_length)

        # Reversed list to go backward with every other iteration
        reversed_x = x_positions[::-1]
    
        # Getting original z to return to 
        z_original = self.scanner_z._position_m
        
        # Opening all scanners and photon counters
        with self.scanner_x as x_con, self.scanner_y as y_con, self.scanner_z as z_con, self.photon_counter as pc:
            # Sets the initial position to be location at the place that the user requested
            z_con.set_position_m(z_position)

            # Iterates through y setting the position once per line 
            for ind_y,y_loc in enumerate(y_positions):
                y_con.set_position_m(y_loc)
                # Flips the even and odd rows so we don't have jumps going back and forth on the x axis 
                if ind_y%2 == 0:
                    for ind_x,x_loc in enumerate(x_positions):
                        x_con.set_position_m(x_loc)
                        counts = pc.get_counts_per_second(dwell_time_s=dwell_time_s)
                        line_counts[ind_x] = counts

                else:
                    for ind_x,x_loc in enumerate(reversed_x):
                        x_con.set_position_m(x_loc)
                        counts = pc.get_counts_per_second(dwell_time_s=dwell_time_s)
                        line_counts[(x_length-1)-ind_x] = counts

                # Adds a full line at a time 
                xy_counts[:,ind_y] = line_counts

            
            # Resetting back to original z position
            z_con.set_position_m(z_original)

        xy_counts = np.rot90(xy_counts)

        return xy_counts,np.array(x_positions),np.array(y_positions)
    
    def z_scan(self,dwell_time_s:float,x_position:float,y_position:float, z_positions:NDArray)->tuple[NDArray,NDArray]:
        """This is a z scan over a stationary xy position. It then goes through the z positions sequential
         after ordering the lists to be in the correct orientation

        Args:
            dwell_time_s (float): How long we dwell at each point before moving to the next point
            x_position (float): An array of the x position you want to scan at 
            y_position (float): An array of the y position you want to scan at 
            z_positions (NDArray): An array of the z positions you want to scan over 

        Returns:
            NDArray: Photon counts. An array of the photons per second at each point in the z positions
            NDArray: Z positions. A sorted array for the z positions 
        """
        # Sorting z list
        z_positions = sorted(z_positions)

        # Preallocating z counts
        photon_counts = np.zeros(len(z_positions))

        # Getting original z to return to 
        z_original = self.scanner_z._position_m
        
        # Opening all scanners and photon counters
        with self.scanner_x as x_con, self.scanner_y as y_con, self.scanner_z as z_con, self.photon_counter as pc:
            
            # Setting the xy position of interest 
            x_con.set_position_m(x_position)
            y_con.set_position_m(y_position)

            # Iterating over all desired z positions 
            for ind_z,z_loc in enumerate(z_positions):
                z_con.set_position_m(z_loc)
                photon_counts[ind_z] = pc.get_counts_per_second(dwell_time_s)

            # Resetting back to original z position
            z_con.set_position_m(z_original)
        
        return photon_counts,np.array(z_positions)
    
    def tracking(self,x_position:float,y_position:float,z_position:float)->tuple[float,float,float,tuple[NDArray,NDArray,NDArray,NDArray,NDArray]]:
        xy_span = self.tracking_xy_span
        z_span = self.tracking_z_span
        dwell_time_s = self.tracking_dwell_time_s
        xy_number_of_points = self.tracking_xy_number_of_points
        z_number_of_points = self.tracking_z_number_of_points

        x_positions = np.linspace(x_position-xy_span/2,x_position+xy_span/2,xy_number_of_points)
        y_positions = np.linspace(y_position-xy_span/2,y_position+xy_span/2,xy_number_of_points)
        z_positions = np.linspace(z_position-z_span/2,z_position+z_span/2,z_number_of_points)


        xy_2d_scan, _ , _ = self.xy_scan(dwell_time_s,x_positions,y_positions,z_position)

        flat_index = np.argmax(xy_2d_scan)

        row_index, col_index = np.unravel_index(flat_index, xy_2d_scan.shape)

        x_pos = x_positions[col_index]
        y_pos = y_positions[xy_number_of_points - row_index - 1]

        z_1d_scan, _ = self.z_scan(dwell_time_s,x_pos,y_pos,z_positions)

        z_pos = z_positions[np.argmax(z_1d_scan)]

        return x_pos,y_pos,z_pos,(xy_2d_scan,z_1d_scan,x_positions,y_positions,z_positions)



