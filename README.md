<h1 align = "center"> GEAR Network Documentation </h1>
The GEAR Network is funded by a $5M grant from the U.S. National Science Foundation’s Research Networks in Mathematical Sciences (RNMS) program.The acronym GEAR stands for GEometric structures And Representation varieties and reflects the mathematical focus of the network (described here).  The GEAR Network brings together researchers from over 90 nodes at mathematics centers throughout the world. 

### Introduction
This documentation serves as a guide on how to use our program to construct network based on publications of GEAR members and generate documents for the GEAR website to visualize the network. 

### Prerequisite
* Python 2.x    
* Packages: `BeautifulSoup, pyprind, json`     
* MathSciNet subscription (e.g. campus internet connection)

#### Windows:   
0. Connect to school wifi    
Useful information: https://answers.uillinois.edu/illinois/page.php?id=47507    
Please choose TunnelAll for "Group"


1. Install Python 2.7    
Download Anaconda https://www.continuum.io/downloads#_windows    
Check "Register Anaconda as my default Python 2.7" in case you have previously installed Python.    
2. Download our package    
You can download this code package by https://codeload.github.com/LargePanda/GEAR_Network/zip/master    
A ZIP file will be downloaded and you need to unzip it.     
3. Run the program     
Navigate to root of the package, open 'scripts', right click "run", choose "Run as Administrator"    
If there are files with valid contents in /output folder, then it runs successfully    
4. Check    
'website_input' folder should have: profile.json, papers.json    
'gephi_input' folder should have co-citation and co-authorship matrices    
5. After get output from Gephi    
Navigate to root of the package, open 'scripts', right click "run_after_gephi", choose "Run as Administrator"    

#### Mac:
Open terminal and type the following lines one by one ending with ENTER    
```
    pip install beautifulsoup4
    pip install pyprind
```

### Execution
* Short Version     

* Complete Version

[ipython notebook version](https://github.com/LargePanda/GEAR_Network/blob/master/GEAR_NETWORK.ipynb)
