
# imports 
import numpy as np # for the actual calculations 
import numpy.typing as npt # for type hinting numpy
import pandas as pd # importing and manipulating the data

import matplotlib.pyplot as plt # plotting the data 
from scipy.optimize import leastsq # fitting the fucntions to the ESR data 

class CwesrAnalysis:

    def __init__(self, frequency_data: npt.ArrayLike, power_level_data: npt.ArrayLike, error_in_pl: npt.ArrayLike):
        # bringing in the data 
        self.frequency_data = frequency_data
        self.power_level_data = power_level_data
        self.error_in_pl = error_in_pl

    def __repr__(self):
        print(self.frequency_data,self.power_level_data)

        
    def lorentzian(self, x, x0, a, gam ):
        return a * gam**2 / ( gam**2 + ( x - x0 )**2)

    def multi_lorentz(self, x, params ):
        off = params[0]
        paramsRest = params[1:]
        assert not ( len( paramsRest ) % 3 )
        return off + sum( [ self.lorentzian( x, *paramsRest[ i : i+3 ] ) for i in range( 0, len( paramsRest ), 3 ) ] )

    def multi_lorentz_with_heating(self, x, params ):
        off = params[0]
        slope = params[1]

        paramsRest = params[2:]

        assert not ( len( paramsRest ) % 3 )
        return off + slope*x + sum( [ self.lorentzian( x, *paramsRest[ i : i+3 ] ) for i in range( 0, len( paramsRest ), 3 ) ] )

    def res_multi_lorentz(self, params, xData, yData ):
        diff = [ self.multi_lorentz( x, params ) - y for x, y in zip( xData, yData ) ]
        return diff

    def res_multi_lorentz_with_heating(self, params, xData, yData ):
        diff = [ self.multi_lorentz_with_heating( x, params ) - y for x, y in zip( xData, yData ) ]
        return diff
    def find_fwhm(self,fit_y):
        #Finding the FWHM this should only be classed when looking at hyperfine or a single NV peak otherwise it will be inaccuarte 
        half_min_curve = max(fit_y)-(max(fit_y)-min(fit_y))/2


        for ind,x in enumerate(fit_y):

            if x < half_min_curve:
                low_ind = ind
                break


        for ind,x in enumerate(reversed(fit_y)):
            if x < half_min_curve:
                high_ind = len(fit_y)-ind
                break
        
        return low_ind, high_ind


    def fit_normal(self,n_dips,export_xy_fit_function = False, number_of_points = 1000):
        
        # Getting data from class
        xData = self.frequency_data
        yData = self.power_level_data/1000 # Reducing the size of the data allows for a more consistent fit. If the Values of x and y are on the same magnitude it is best

        # General fitting Parameters 
        generalWidth = 1
        yDataLoc = yData
        
        #Initializing guessing list
        startValues = [ max( yData )]

        for i in range(n_dips):

            minP = np.argmin( yDataLoc )
            minY = yData[ minP ]
            x0 = xData[ minP ]
            startValues += [ x0, minY - max( yDataLoc ), generalWidth ]

            popt, ier = leastsq( self.res_multi_lorentz, startValues, args=( xData, yData ) )
            yDataLoc = [ y - self.multi_lorentz( x, popt ) for x,y in zip( xData, yData ) ]

        if export_xy_fit_function:
            fit_x = np.linspace(min(xData),max(xData),number_of_points)
            fit_y = [ self.multi_lorentz(x, popt ) for x in fit_x ]

            return popt, fit_x, fit_y
        else:
            return popt  

    def fit_heated(self,n_dips,export_xy_fit_function = False, number_of_points = 1000):
        
        # Getting data from class
        xData = self.frequency_data
        yData = self.power_level_data/1000 # Reducing the size of the data allows for a more consistent fit. If the Values of x and y are on the same magnitude it is best

        # General fitting Parameters 
        generalWidth = 1
        yDataLoc = yData
        slope = -10
        
        #Initializing guessing list
        startValues = [ max( yData ) , slope]

        for i in range(n_dips):

            minP = np.argmin( yDataLoc )
            minY = yData[ minP ]
            x0 = xData[ minP ]
            startValues += [ x0, minY - max( yDataLoc ), generalWidth ]

            popt, ier = leastsq( self.res_multi_lorentz_with_heating, startValues, args=( xData, yData ) )
            yDataLoc = [ y - self.multi_lorentz_with_heating( x, popt ) for x,y in zip( xData, yData ) ]

        
        if export_xy_fit_function:
            fit_x = np.linspace(min(xData),max(xData),number_of_points)
            fit_y = [ self.multi_lorentz_with_heating(x, popt ) for x in fit_x ]

            return popt, fit_x, fit_y
        else:
            return popt  
    
    def plot_heated_fit(self, n_dips, calculate_fwhm = False,title=None, x_label = "Frequency(MHz)", y_label = "NV Counts (kCounts/S)"):
        
        # Getting fit data 
        output,frequency,fitted_curve = self.fit_heated(n_dips,export_xy_fit_function=True)

        # Printing off data in human readable style
        print("Y Offset: %5.2f, Heating Slope: %5.2f"%(output[0],output[1]))
        print("Estimated Offset for PL: %5.2f"%(output[0]+output[1]*output[2]))
        for i in range(int((len(output)-2)/3)):
            print("Center:%5.2f, Amplitude: %5.2f, G: %5.2f"%(output[i*3+2],output[i*3+3],output[i*3+4]))

        #Getting data
        frequency_data = self.frequency_data
        power_level_data = self.power_level_data
        error_in_pl = self.error_in_pl

        fig = plt.figure()

        # If we want to find the full width half maximum of the function
        if calculate_fwhm:
            low_ind, high_ind = self.find_fwhm(fitted_curve)
            plt.scatter([frequency[low_ind],frequency[high_ind]],[fitted_curve[low_ind],fitted_curve[high_ind]],zorder = 10,label = "FWHM",alpha=0.6,c="RED")

            print("The Estimated FWHM: %5.2f"%(frequency[high_ind]-frequency[low_ind]))

       
        
        #plotting functions 
        plt.plot(frequency,fitted_curve,"--",c="black",label="Fitted Function",zorder=3)
        plt.plot(frequency_data, power_level_data/1000, color='peachpuff',linewidth=2,zorder=2,label="Average Counts")

        # Adding in the error shading for the plot
        error_high = power_level_data+error_in_pl
        error_low = power_level_data-error_in_pl
        x = np.concatenate((frequency_data,frequency_data[::-1]))
        y = np.concatenate((error_high,error_low[::-1]))/1000

        plt.fill(x,y,"coral",zorder=1,alpha=0.5, label = "Error")

        #Formatting for the figure 
        plt.ylabel(y_label)
        plt.xlabel(x_label)
        plt.title(title)
        plt.legend()
        
        plt.show(block=False)

    def plot_fit(self, n_dips, calculate_fwhm = False,title=None, x_label = "Frequency(MHz)", y_label = "NV Counts (kCounts/S)"):
        
        # Getting fit data 
        output,frequency,fitted_curve = self.fit_normal(n_dips,export_xy_fit_function=True)

        # Printing off data in human readable style
        print("Y Offset: %5.2f"%(output[0]))
        for i in range(int((len(output)-2)/3)+1):
            print("Center:%5.2f, Amplitude: %5.2f, G: %5.2f"%(output[i*3+1],output[i*3+2],output[i*3+3]))

        #Getting data
        frequency_data = self.frequency_data
        power_level_data = self.power_level_data
        error_in_pl = self.error_in_pl

        fig = plt.figure()
        # If we want to find the full width half maximum of the function
        if calculate_fwhm:
            low_ind, high_ind = self.find_fwhm(fitted_curve)
            plt.scatter([frequency[low_ind],frequency[high_ind]],[fitted_curve[low_ind],fitted_curve[high_ind]],zorder = 10,label = "FWHM",alpha=0.6,c="RED")

            print("The Estimated FWHM: %5.2f"%(frequency[high_ind]-frequency[low_ind]))

        #plotting functions 
        plt.plot(frequency,fitted_curve,"--",c="black",label="Fitted Function",zorder=3)
        plt.plot(frequency_data, power_level_data/1000, color='peachpuff',linewidth=2,zorder=2,label="Average Counts")

        # Adding in the error shading for the plot
        error_high = power_level_data+error_in_pl
        error_low = power_level_data-error_in_pl
        x = np.concatenate((frequency_data,frequency_data[::-1]))
        y = np.concatenate((error_high,error_low[::-1]))/1000

        plt.fill(x,y,"coral",zorder=1,alpha=0.5, label = "Error")

        #Formatting for the figure 
        plt.ylabel(y_label)
        plt.xlabel(x_label)
        plt.title(title)
        plt.legend()
        
        plt.show(block=False)
    
    @classmethod
    def data_from_matlab_output(cls,file_path):
        # Simple method for making the class using data that is output from the standard matlab program
        data = pd.read_csv(file_path,sep="\t")
        frequency = data["Frequency"]
        average_counts = data["AverageCountRate"]
        error_in_pl = data["Error"]

        return cls(frequency,average_counts,error_in_pl)