__all__ = ["DataManager"]
"""This module is meant to allow for a standard way to import and export data to python and matlab 
"""
from enum import Enum
import os 
import datetime
import fnmatch
import uuid
import h5py
from dataclasses import dataclass
import time

from NV_ABJ.experimental_logic.sequence_generation.sequence_generation import Sequence
class DataManager:
    class file_type:
        hdf5:str = "hdf5"
        # Not implemented yet
        # csv = "csv"
        # txt = "txt"
        # json = "json"
    
    @dataclass
    class attributes:
        # These should generally be filled pout by the user 
        sample:str # Identifiable sample name 
        diamond:str # Identifiable diamond name 
        nv_orientation:list[int] # Orientations of the NV(s) in question 
        setup_notes:str





    def __init__(self, default_save_location:str,sample:str = None,diamond:str = None,nv_orientation:list[int] = None,setup_notes:str = None,
                  default_save_type=file_type.hdf5, uuid_length:int = 10):
        self.default_save_location = default_save_location
        self.default_save_type = default_save_type
        self.uuid_length = uuid_length

        self._attr = DataManager.attributes(sample,diamond, nv_orientation,setup_notes)


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
    
    def save_hdf5(self, data_dict:dict,measurement_parameters_dict:dict=None,folder_path:str=None,file_path:str=None)-> str:
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

        data_tag = measurement_parameters_dict["measurement_name"]

        if data_tag == None:
            data_tag = self.__class__.__name__

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
                if str(data_to_save := data_dict[data_key]) != str(None):
                    f.create_dataset(str(data_key), data = data_to_save)#, compression='gzip')

            if measurement_parameters_dict != None:
                for data_key in measurement_parameters_dict:
                    if str(data_to_save := measurement_parameters_dict[data_key]) != str(None):
                        print(data_to_save)
                        f.create_dataset(str(data_key), data = data_to_save)

            # Adding attributes to file if needed
            if self._attr != None:
                for attribute_key in self._attr.__dict__:
                    if (attr_value := self._attr.__dict__[attribute_key]) != None:
                        print(attr_value)
                        f.attrs[attribute_key] = attr_value
            

            
        return _file_path
    
    def load_hdf5(self, file_path:str):

        data_dict = {}

        with h5py.File(file_path, 'r') as f: 
            data_set_names = f.keys()
            for data_name in data_set_names:
                data_dict[data_name] = f[data_name][()]
    
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
        attributes = {}
        for attr_key in attr.__dict__.keys():
            if attr.__dict__[attr_key] != None:
                attributes[attr_key] = attr.__dict__[attr_key]
        attributes_keys = attributes.keys()
        
        dir_list = os.listdir(folder_path)

        file_paths = []

        for file in dir_list:
            add_path = True
            try:
                with h5py.File(os.path.join(folder_path,file), 'r') as f: 

                    for attribute_key in attributes_keys:
                        if not (attributes[attribute_key] in f.attrs[attribute_key]):
                            add_path = False                            
                if add_path:
                    file_paths.append(file)
            except:
                pass

        return file_paths


    def save_measurement_sequence_data(self, data_dict:dict,measurement_name:str,measurement_class_inputs:dict[str:any],sequence_class:Sequence,number_of_measurements_per_point:int,
                  number_of_points_per_sweep:int,number_of_sweeps:int,measurement_notes:str = None,file_type:file_type=None):
        # These should be auto filled out by the measurement class called 
        self.time_of_save:float = time.time()

        if file_type == None:
            file_type = self.default_save_type

        protected_names = ["SequenceClass","MeasurementNotes"]

        for name in protected_names:
            if name in data_dict.keys():
                raise NameError(f"You can not use the name:{name} in your data dictionary please select a different name. Protected Names:{protected_names}")
        
        # data_dict["SequenceClass"] = sequence_class.instructions()
        data_dict["MeasurementNotes"] = measurement_notes
        
        measurement_parameters = {"measurement_name":measurement_name,
                                  "measurement_class_inputs":measurement_class_inputs,
                                  "number_of_measurements_per_point":number_of_measurements_per_point,
                                  "number_of_points_per_sweep":number_of_points_per_sweep,
                                  "number_of_sweeps":number_of_sweeps,
                                  }

    
        if file_type == DataManager.file_type.hdf5:
            self.save_hdf5(data_dict=data_dict,measurement_parameters_dict=measurement_parameters)
        else:
            raise NotImplementedError(f"The requested file type{_} does not have an implemented save functionality")


if __name__ == "__main__":

    import numpy as np
    from NV_ABJ.experimental_logic.sequence_generation.sequence_generation import *
    number_samples = int(20e3*200*15)
    print(number_samples)
    data = np.linspace(0,10_000_000,10_000_000)

    data_manager = DataManager(default_save_location=r"C:\Users\LTSPM2\Desktop",
                               sample="Sample Test",
                               diamond="Diamond Test",
                               )
    dev1 = SequenceDevice(0)
    
    seq = Sequence()
    seq.add_step(2000, [dev1])
    
    data_manager.save_measurement_sequence_data(data_dict={"Numbers":data},
                                                measurement_class_inputs=[1,2,5],
                                                measurement_name="Random Measurement",
                                                sequence_class=seq,
                                                number_of_measurements_per_point=10,
                                                number_of_points_per_sweep=100 ,
                                                number_of_sweeps=10)
    
    # print(data_manager.load_hdf5(r"C:\Users\LTSPM2\Desktop\2025-05-08\Random Measurement_1_806cbd464b.hdf5"))