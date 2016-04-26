<h1 align = "center"> GEAR Network Documentation </h1>
The GEAR Network is funded by a $5M grant from the U.S. National Science Foundation’s Research Networks in Mathematical Sciences (RNMS) program.The acronym GEAR stands for GEometric structures And Representation varieties and reflects the mathematical focus of the network (described here).  The GEAR Network brings together researchers from over 90 nodes at mathematics centers throughout the world. 

### Introduction
This documentation serves as a guide on how to use our program to construct network based on publications of GEAR members and generate documents for the GEAR website to visualize the network. 

### Prerequisite
* Python 2.x    
* Packages: `networkx, liternet, scrapy, BeautifulSoup, pyprind, json, matplotlib`     
* MathSciNet subscription (e.g. campus internet connection)

### Execution
* Short Version     

1. Generate Matrix    
```
    git clone git://github.com/dasmith/stanford-corenlp-python.git
    cd stanford-corenlp-python
    python run.py matrix
```
2. Clustering by Gephi     
3. Generate input for webpage    
(Navigate to GEAR_Network/)    
```
    python run.py webpage
```
* Complete Version

[ipython notebook version](https://github.com/LargePanda/GEAR_Network/blob/master/GEAR_NETWORK.ipynb)
