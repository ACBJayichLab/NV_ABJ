
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

        This is in the form of a numpy array
            two_tau = the tau time given in the files 
            normalized_data = the raw normalized data from the files 

        """
        self.two_tau = two_tau
        self.normalized_data = normalized_data
    

    @property
    def average_norm(self):
        # Takes the average of the normalized data
        return self.normalized_data.mean(axis=0)
    
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