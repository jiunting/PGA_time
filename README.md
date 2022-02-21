# analysis PGA timing

![GitHub last commit](https://img.shields.io/github/last-commit/jiunting/PGA_time?style=plastic)  

### PGA timing analysis tool

****

* [1. Installation](#1-installation)


****
## 1. Installation
#### 1.1 cd to the place where you want to put the source code, then clone the repository  
    cd Your_Local_Path  
and  

    git clone https://github.com/jiunting/PGA_time.git

#### 1.2. create conda env and install libcomcat: https://github.com/usgs/libcomcat
    conda create -n PGA_time --channel conda-forge python=3.9
    conda activate PGA_time
    conda config --add channels conda-forge
    conda install libcomcat
    
#### 1.3. install dependent package
    pip install bs4
    
#### 1.4. ready to install the main package
    pip install -e .
    
   
    
