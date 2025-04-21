__all__ = ["DataManager"]
"""This module is meant to allow for a standard way to import and export data to python and matlab 
"""
from enum import StrEnum
import os 
import datetime
import fnmatch
import uuid
import h5py

class DataManager:
    class file_type(StrEnum):
        hdf5 = "hdf5"
        # Not implemented yet
        # csv = "csv"
        # txt = "txt"
        # json = "json"
    

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
    
    def save_hdf5(self,data_tag:str, data_dict:dict,file_attributes:dict = None,folder_path:str=None,file_path:str=None)-> str:
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
            if file_attributes != None:
                for attribute_key in file_attributes:
                    f.attrs[attribute_key] = file_attributes[attribute_key]
            
        return _file_path
    
    def load_hdf5(self, file_path:str):

        with h5py.File(file_path, 'r') as f: 
            print(f.attrs.keys())



        






if __name__ == "__main__":
    data_manager = DataManager(r"C:\Users\LTSPM2\Desktop\test")
    import numpy as np
    arr = np.random.randn(1000)

    data = {"data":arr}

    attributes = {"description": "CWESR", "points":"100","averages":"20"}

    for i in range(100):
        file_path = data_manager.save_hdf5(data_dict=data,data_tag="name", file_attributes=attributes)
        print(file_path)

    data_manager.load_hdf5(r"C:\Users\LTSPM2\Desktop\test\2025-04-21\name_100_1cdab32732.hdf5")

        

