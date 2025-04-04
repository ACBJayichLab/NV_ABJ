import os, shutil, tempfile

# This returns the command line to its original location 
src_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)))
try:
    # Creates temporary directory 
    directory = tempfile.TemporaryDirectory(prefix="ABJ_Module_Installer_")
    #Copy all the files from the directory that the __main__.py file is in 
    src = os.path.dirname(os.path.realpath(__file__))
    # Destination directory is where the files are copied into a sub folder in the temp 
    dest = os.path.join(directory.name,"src") 

    shutil.copytree(src, dest) # Copies files over 
    os.chdir(dest) # Changes command line to be in the new directory 
    os.system("pip install --upgrade build") # Upgrades the build package
    os.system("python -m build") # Builds the package in the temp directory 
    os.system("pip install .") # Installs the new package that was just built
    os.chdir(src_dir) # Changes working directory back to original file location

except Exception as e:
    print("Failed to add to library",e)

finally:
    directory.cleanup() # executes each time
    print(f'The temporary directory: "{directory.name}" has been cleaned up')

