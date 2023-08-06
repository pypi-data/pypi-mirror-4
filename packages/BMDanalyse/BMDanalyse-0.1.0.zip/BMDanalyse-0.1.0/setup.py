
from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup

setup(
    name = 'BMDanalyse',
    version = '0.1.0',
    description = 'Tool to analyse regional changes in a time series of 2D medical images.',
    license = 'MIT license',
    keywords = "python medical image analysis ROIs",    
    author = 'Michael Hogg',
    author_email = 'michael.christopher.hogg@gmail.com',
    url = "http://pypi.python.org/pypi/BMDanalyse/",
    download_url = "https://pypi.python.org/packages/source/B/BMDanalyse/BMDanalyse-0.1.0.zip",
    packages = ['BMDanalyse'],
    package_data = {'BMDanalyse': ['icons/*','sampleMedicalImages/*']},
    entry_points = { 'console_scripts': ['BMDanalyse = BMDanalyse.BMDanalyse:run',]},
    classifiers = [
        "Programming Language :: Python",                                  
        "Programming Language :: Python :: 2",             
        "Programming Language :: Python :: 2.7",                                                    
        "Development Status :: 4 - Beta",                                  
        "Environment :: Other Environment", 
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",   
        "License :: OSI Approved :: MIT License", 
        "Operating System :: OS Independent",     
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Visualization",
        ],
    long_description = """
About
-----

A tool used for the regional analysis of a time series of 2D medical images, typically X-rays or virtual X-rays (output from a computer simulation).
Intended to be used to evaluate the bone gain / loss in a number of regions of interest (ROIs) over time, typically due to bone remodelling as a result of stress shielding around an orthopaedic implant.
    
Written in pure Python using PyQt4/PySide, pyqtgraph, numpy, scipy and matplotlib. Should work on any platform, but has only been tested on Windows.

How to use
----------

Load a time series of 2D medical images (in image format such as bmp, png etc). Use the up / down arrows below the image file list to place the images in chronological order. 
A time series of virtual X-rays is provided in the sampleMedicalImages directory. 

From here, there are two main functions:

1. **ROI analysis**
   
   Create a number of Regions of Interest (ROI) over the top of the images. This can be done by using the ROI toolbox, or by right clicking within the image box. 
   
   Left click on an ROI to make current / deactivate. When current (green colour), ROI can be translated, rotated and resized. More specifically:
   
   - To translate: Hold down left mouse button and drag
   - To rotate: Left click one of the ROI corner handles and drag
   - To resize: Left click one of the ROI mid-side handles and drag
   
   Note that ROIs can be copied saved to disk, loaded from disk. Right click on the current ROI to show its menu.
   
   From the toolbar, select *Analyse -> ROI analysis*. This displays a plot of the change in the average grey scale value of each ROI over time. 
   The data can be edited using *"Edit plot"* and exported to csv file using *"Export data"*.
   
   A screen capture of the image box (showing the current medical image and ROIs) can be exported to file by right clicking on the image box and selecting *"Export image"* from the pop-up menu.

2. **Image analysis**

   From the toolbar, select *Analyse -> Image analysis*. This displays a new dialog box with contours of change (relative to the first image in the series). 
   Use the left / right arrows to cycle through all the images. Use the slider to adjust the amount of change required i.e. a value of 10% will display regions of loss >= 10% (shown in blue) AND regions of gain >= 10% (shown in red).    

   A screen capture of the image box (showing the current medical image and gain / loss contours) can be exported to file by right clicking on the image box and selecting *"Export image"* from the pop-up menu.
""",

    install_requires = [
        'pyqtgraph',        
        'matplotlib',
        'numpy',
        'scipy',
        ],
)
