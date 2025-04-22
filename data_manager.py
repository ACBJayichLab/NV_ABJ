__all__ = ["DataManager"]
"""This module is meant to allow for a standard way to import and export data to python and matlab 
"""
from enum import StrEnum
import os 
import datetime
import fnmatch
import uuid
import h5py
from dataclasses import dataclass

from NV_ABJ.experimental_logic.sequence_generation.sequence_generation import Sequence
class DataManager:
    class file_type(StrEnum):
        hdf5 = "hdf5"
        # Not implemented yet
        # csv = "csv"
        # txt = "txt"
        # json = "json"
    
    @dataclass
    class attributes:
        # These should generally be filled pout by the user 
        sample:str = None # Identifiable sample name 
        diamond:str = None # Identifiable diamond name 
        nv_orientation:list[int] = None # Orientations of the NV(s) in question 
        notes:str = None

        # These should be auto filled out by the measurement class called 
        _measurement_class_name:str = None # This is the name of the class used to measure in python __name__ 
        _measurement_class_inputs:dict[str:any] = None # This is going to be what inputs were to go into the measurement class {kwarg0:value0, kwarg1:value1,...}
        _sequence_class:Sequence = None # This is the sequence class for the measurement 
        _number_of_measurements_per_point:int = None # How many times you average at a point before moving on to the next 
        _number_of_points_per_sweep:int = None # How many points for a given sweep
        _number_of_sweeps:int = None # How many sweeps for the overall average
        _time_of_measurement:float = None # Seconds from epoch saved 




    def __init__(self, default_save_location, default_save_type=file_type.hdf5, uuid_length:int = 10):
        self.default_save_location = default_save_location
        self.default_save_type = default_save_type
        self.uuid_length = uuid_length

        # Checking for default location and creating it if it doesn't exist  
        if not os.path.exists(default_save_location):
            os.mkdir(default_save_location)

    def create_file_id(self,data_tag:str, file_type:file_type, folder_path:str=None)->str:
        """This function checks for he folders to make sure they exist then generates a unique file 
        path that can be used to save the data at

        Args:
            data_tag (str): The type of data one could reasonably expect when opening the folder. etc. CWESR, Rabi,...
            file_type (file_type): type of file intended to be saved 
            folder_path (str, optional): Allows you to overwrite the default save locations. Default None to save in default location

        Returns:
            str: unique file path 
        """
        today = str(datetime.date.today())
        if folder_path == None:
            _folder_path = os.path.join(self.default_save_location, today)
        else:
            _folder_path = os.path.join(folder_path, today)


        # Creating folder if it doesn't exist 
        if not os.path.exists(_folder_path):
            os.mkdir(_folder_path)
        
        # Creating time stamp
        uuid_name = str(uuid.uuid4())[-self.uuid_length:]
        count_name = len(fnmatch.filter(os.listdir(_folder_path), f'*.{file_type}'))+1

        # Creating the file path and names 
        file_name = f"{data_tag}_{count_name}_{uuid_name}.{file_type}"
        file_path = os.path.join(_folder_path,file_name)


        
        return file_name, file_path
    
    def save_hdf5(self, data_dict:dict, attr:attributes = None,folder_path:str=None,file_path:str=None)-> str:
        """This is the save method for the hdf5 format it takes a dictionary of data but is also able to take a list of
        attributes to make searching easier, a folder path if you don't want to save it as the default folder and a 
        file path if you want overwrite the default file save mechanism. File path will override the folder path and file extension 
        but will save it as a HDF5 so do not enter "file_name" you must enter something similar to "folder_location/file_name.hdf5"


        Args:
            data_dict (dict): dictionary of data you wish to save
            file_attributes (dict, optional): list of attributes you wish to associate with the file. Defaults to None.
            folder_path (str, optional): Change from default save location method. Defaults to None.
            file_path (str, optional): Change folder, filename, and extension from default method. Defaults to None.

        Returns:
            str: file path 
        """
        data_tag = str(attr.__dict__["_measurement_class_name"])

        if folder_path == None and file_path == None:
            # Default  save method 
            _, _file_path = self.create_file_id(data_tag=data_tag,file_type=DataManager.file_type.hdf5.value)
        elif file_path != None:
            # If we have an overall rewrite
            _file_path = file_path
        else:
            # If the folder location has been over written 
            file_name, _ = self.create_file_id(data_tag=data_tag,file_type=DataManager.file_type.hdf5.value)
            _file_path = os.path.join(folder_path,file_name)


        # creating a file
        with h5py.File(_file_path, 'w') as f: 
            for data_key in data_dict:
                f.create_dataset(str(data_key), data = data_dict[data_key])

            # Adding attributes to file if needed
            if attr != None:
                for attribute_key in attr.__dict__:
                    if (attr_value := attr.__dict__[attribute_key]) != None:
                        f.attrs[attribute_key] = attr_value
            
        return _file_path
    
    def load_hdf5(self, file_path:str):

        data_dict = {}

        with h5py.File(file_path, 'r') as f: 
            data_set_names = f.keys()
            for data_name in data_set_names:
                data_dict[data_name] = f[data_name][:]
    
        return data_dict
    

    def search_for_hdf5(self, folder_path:str, attr:attributes)->list[str]:
        """This searches through a folder only to a single level down and filters 
        through the file attributes that to find ones that match what you are looking for.
        This then returns a list of file paths for anything that matches 

        Args:
            folder_path (str): A path to the folder you want to search through
            attr (attributes): Attributes we would like to match using the attributes class in DataManager

        Returns:
            list[str]: list of file paths where the attributes match
        """
        with h5py.File(file_path, 'r') as f: 
            print(f.attrs.keys())



        






if __name__ == "__main__":
    data_manager = DataManager(r"C:\Users\schwa\Desktop\New folder")
    import numpy as np
    arr = np.random.randn(1000)

    data = {"data":arr}

    attr = DataManager.attributes()
    attr.diamond = "L036"
    attr.sample = "NbN CPW V3"
    attr.nv_orientation = [111,101]

    # print(attr.__dict__.keys())


    # for i in range(100):
    #     file_path = data_manager.save_hdf5(data_dict=data, attr=attr)
    #     print(file_path)

    print(data_manager.load_hdf5(r"C:\Users\schwa\Desktop\New folder\2025-04-22\None_100_8294970afd.hdf5"))

        

