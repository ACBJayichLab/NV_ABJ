# NV_ABJ

This is a base conversion from matlab to a pythonic system that uses qudi to operate the experimental aparatus

# Installing

Make sure you are running the correct python version (3.10) and run the "_ _ main _ _.py" file to install this package

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
