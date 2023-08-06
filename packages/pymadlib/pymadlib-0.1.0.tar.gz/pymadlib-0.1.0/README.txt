================================================================================
Python wrapper for MADlib 
Srivatsan Ramanujam <vatsan.cs@utexas.edu>, 3 Jan 2013
This currently implements Linear regression, Logistic Regression, 
SVM (regression & classification), K-Means and LDA algorithms of MADlib.
Refer : http://doc.madlib.net/v0.5/ for MADlib's user documentation.
================================================================================

Dependencies : 
===============
You'll need the python extension : psycopg2 to use PyMADlib.
  (i)  If you have matplotlib installed, you'll see Matplotlib visualizations for Linear Regression demo.
 (ii)  If you have installed networkx (http://networkx.github.com/download.html), you'll see a visualization of the k-means demo
(iii)  PyROC (https://github.com/marcelcaraciolo/PyROC) is included in the source of this distribution with permission from its developer. You'll see a visualization of the ROC curves for Logistic Regression.

Configurations:
===============
To configure your DB Connection parameters
You should create a file in your home directory : ~/.pymadlib.config 
that should look like so :

------------------------------------------------------------
[db_connection]
user = gpadmin
password = XXXXX
hostname = 127.0.0.1 (or the IP of your DB server)
port = 5432 (the port# of your DB)
database = vatsandb (the database you wish to connect to)
------------------------------------------------------------

INSTALLATION INSTRUCTIONS:
===========================
Run (after unzipping the tarball & cd'ing into the code directory):
     sudo python setup.py build
     sudo python setup.py install

Datasets packaged with this installation :
=========================================
PyMADlib packages publicly available datasets from the UCI machine learning repository and other sources.

1) Wine quality dataset from UCI Machine Learning repository : http://archive.ics.uci.edu/ml/datasets/Wine+Quality
2) Auto MPG dataset from UCI ML repository : http://archive.ics.uci.edu/ml/datasets/Auto+MPG
3) Obama-Romney second presidential debate (2012) transcripts for the LDA models. 

