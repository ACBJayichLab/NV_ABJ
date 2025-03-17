# NV_ABJ

This is a base conversion from matlab to a pythonic system that uses qudi to operate the experimental aparatus

# Installation

Using anaconda as the library manager rather than pip alone enter into the command line

```
conda create -n py310 python=3.10
conda activate py310
```

On your code IDE make sure you've selected the correct python version in VSCode this is just done by selecting python interpreter in the search bar "*> Python: Select interpretor*"

You likely will need to go into the anaconda navigator select enviroments and change the enviroment running from base to py310. This is beacuse it will run python 3.10 in your interpretor but will run the base in your powershell so you can install packages but a pip install will install under the base python and not the desired version

Run the "_ _ main _ _.py" file to install this package

- It creates a temporary directory in your computer which it builds a directory in and installs into your pip library
- If an error occurs it should still clean up the directory but if there is an error you may see a folder in your temporary files location with *ABJ_Module_Installer_* as a prefix
- This method of installation removes the distribution package accross the systems and should also standardize between systems

## Requirements

Python 3.10

### Installed Packages

# Methodology

# Python

## Deprecating parts of the code

**Don't just delete it or have it error out!**

```
from warnings import deprecated 


@deprecated("Deprecation message here")
def funct(x,y,z):
	pass
```
