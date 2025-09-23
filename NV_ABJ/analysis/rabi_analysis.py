
import os
from os import listdir
from os.path import isfile, join

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


class RabiAnalysis:
    def __init__(self,two_tau,raw_signal,raw_ref,normalized_data):
        """
        The initial fit  functions for this code were don using Taylors code later modified into a class by Aaron

        driving_frequency = frequency we are driving the microves at in MHz
        microwave_power = how hard we are driving from the SRS in dB
        probe_distance = how far the probe is from the sample or item of intrest in nm
        probe_identifier = the name of the probe for example "L036-E7"
        sample_identifier = the name of the sample for example "NbN CPW V3"

        This is in the form of a numpy array
            two_tau = the tau time given in the files 

        These are in the form of pandas dataframes with the order they were taken in labeled by the columns using integers
            raw_signal = the raw signal data given in the files
            raw_ref = the raw refrence data given in the files 
            normalized_data = the raw normalized data from the files 

                0          1          10         11        12         13        14        15        16  ...        91        92         93        94        95        96        97        98         99
            0   166.5429  147.28570   93.42857  143.82860  163.9429  126.88570  149.3143  158.0571  172.4571  ...  152.4000  167.5429  145.20000  139.5429  158.4000  200.7143  186.6571  154.9714  148.74290
            1   174.1429  147.65710   89.48571  143.97140  165.2571  125.05710  170.3143  160.7143  161.2857  ...  143.9429  177.2286  138.65710  151.1714  155.5143  199.1143  198.3714  146.6000  146.54290
            2   169.8000  136.60000   93.08571  104.60000  159.8857  114.85710  180.9429  161.0571  156.6000  ...  153.0857  166.1143  131.60000  149.1714  155.8000  182.3429  195.7714  158.9429  137.28570
            3   167.3143  124.62860   80.57143   88.97143  153.2857  111.62860  177.6286  169.3429  145.6571  ...  145.7714  164.4571  122.48570  138.8000  155.6571  172.4571  195.7143  158.6286  134.54290
                    
        """
        self.two_tau = two_tau
        self.raw_signal = raw_signal
        self.raw_ref = raw_ref
        self.normalized_data = normalized_data
    
    @property
    def average_reference(self):
        # Takes the average of the reference data
        return self.raw_ref.mean(axis=0)
    @property
    def average_norm(self):
        # Takes the average of the normalized data
        return self.normalized_data.mean(axis=0)
    @property
    def average_signal(self):
        # Takes the average of the signal data
        return self.raw_signal.mean(axis=0)
    
    @property
    def standard_error(self):
        # Takes the standard error from the normalized data
        return self.normalized_data.std(axis=0)
    
    def plot_rabi_data(self, title=None, x_label = "Time (ns)", y_label = "Contrast"):
        # Produces a basic scatter plot of the rabi data without a fit
        average_norm = self.normalized_data.mean(axis=0)
        error_bars = self.normalized_data.std(axis=0)
        print(len(self.two_tau),len(average_norm),len(error_bars))

        plt.errorbar(self.two_tau/2, average_norm, yerr=error_bars, fmt='o', color='peachpuff', ecolor='coral', capsize=5, 
              elinewidth=2, markeredgewidth=2, markeredgecolor='coral', label='Points', markersize = 5, zorder  = 2 )
        
        plt.ylabel(y_label)
        plt.xlabel(x_label)
        plt.title(title)

        plt.show(block = False)

    def plot_rabi_data_with_fit(self, number_fit_points:int = 1000,pi_t_guess:float = 120, phi_guess:float = 0, t2_guess:float = 1000, title=None, x_label = "Time (ns)", y_label = "Contrast"):
        
        pi_t, A, c, phi, lambda_, contrast, pi_time, pi_half_time, pi_three_half_time, delta_pl,fit_x, fit_y = self.fit_rabi_oscillations(generate_fit_function=True,
                                                                                                                                            number_fit_points=number_fit_points,
                                                                                                                                            pi_t_guess=pi_t_guess,
                                                                                                                                            phi_guess=phi_guess,
                                                                                                                                            t2_guess=t2_guess)

        #Plotting the data and the fitted curve
        plt.figure()
        plt.plot(fit_x, fit_y,"--", label='Fitted curve', color='black', zorder = 1)
        plt.errorbar(self.two_tau/2, self.average_norm, yerr=self.standard_error, fmt='o', color='peachpuff', ecolor='coral', capsize=5, 
                    elinewidth=2, markeredgewidth=2, markeredgecolor='coral', label='Points', markersize = 5, zorder  = 2 )


        #This prints the data associated with a rabi fit becuase that is what __repr__ is currently set to 
        print(f"Pi Time: {pi_time}\nPi half time: {pi_half_time}\nPi Three half time: {pi_three_half_time}\nDelta PL: {delta_pl}\nContrast: {contrast}\nLambda: {lambda_}")
        
        plt.ylabel(y_label)
        plt.xlabel(x_label)
        plt.title(title)

        plt.show(block=False)



    def long_rabi_fit(self, t, pi_t, A, c, phi, t2):
    
        decay = A * np.exp(-t / t2)
        oscillation = np.cos(np.pi * (t + phi) / pi_t)
        return (decay * oscillation + c)

    def fit_rabi_oscillations(self, generate_fit_function = False, number_fit_points = 1000,pi_t_guess = 120, phi_guess = 0, t2_guess = 1000):
        # Gathering basic class data 
        x_data = self.two_tau/2
        y_data = self.normalized_data.mean(axis=0)

        refMean = np.mean(self.raw_ref.mean(axis=0))

        # Guessing initial parameters based on data
        A_guess = (np.max(y_data) - np.min(y_data)) / 2
        c_guess = np.mean(y_data)


        initial_guess = [pi_t_guess, A_guess, c_guess, phi_guess, t2_guess]
            
        # Curve fitting
        params, params_covariance = curve_fit(self.long_rabi_fit, x_data, y_data, p0=initial_guess , maxfev=50000)
        
        
        # Fitted parameters
        pi_t, A, c, phi, lambda_ = params

   
        contrast = (2*A)/(c+A)*100
        pi_time = pi_t-phi
        pi_half_time = pi_t/2-phi
        pi_three_half_time = 3*pi_t/2-phi
        
        delta_pl =refMean*contrast/100

        if generate_fit_function:
            # Generate the fitted curve
            fit_x = np.linspace(0, max(x_data), number_fit_points)
            fit_y = self.long_rabi_fit(fit_x, *params)

            return pi_t, A, c, phi, lambda_, contrast, pi_time, pi_half_time, pi_three_half_time, delta_pl,fit_x, fit_y

        else:
            return pi_t, A, c, phi, lambda_, contrast, pi_time, pi_half_time, pi_three_half_time, delta_pl
        
    def __repr__(cls):
        pi_t, A, c, phi, lambda_, contrast, pi_time, pi_half_time, pi_three_half_time, delta_pl = cls.fit_rabi_oscillations()


        return f"Pi Time: {pi_time}\nPi half time: {pi_half_time}\nPi Three half times: {pi_three_half_time}\nDelta PL: {delta_pl}\nContrast: {contrast}\nLambda: {lambda_}"