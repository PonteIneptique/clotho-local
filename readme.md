#Clotho
This project is originally developed by Thibault Clerice. It is open source and so feel free to make pull request, report issues, fork...

This project aims to create network of occurences and auctoritas using Perseus data. 

##License and authorship
- The file `/morph/latin.morph.xml` is distributed with the Perseus Hopper source, which is (according only to the sourceforge project listing) licensed under the Mozilla Public License 1.1 (MPL 1.1)
- The file `/morph/stopwords.txt` comes from http://wiki.digitalclassicist.org/Stopwords_for_Greek_and_Latin

##Installation for Ubuntu / Debian 

Installation has been a lot simplified ! You can know download all dependencies with setup.py !

If you don't have git : `sudo apt-get install git` and of course if you don't have python `sudo apt-get install python`

```
	mkdir ~/dev
	cd ~/dev
	git clone https://github.com/PonteIneptique/clotho-local.git
	cd clotho-local
```

#Installing dependencies
    As we use MySQL for some export, you'll need to install following package on Linux : `apt-get install build-essential python-dev libmysqlclient-dev`

    A graphical library, MatPlotLib, has issues with non-python dependencies, we recommend for Unix Users to do a `apt-get build-dep matplotlib`. You might have to activate Code Source Repository in Mint (In Software Sources)or add the Universe repository in Ubuntu for this command to run fine.

    The pip install for scipy seems to have difficulties, so please use `apt-get install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose` if you are a Linux user (Debian/Ubuntu/Mint)

	As for version 0.1.2, I introduced an install shortcut through pip. To use it, in a terminal press :

```
	cd ~/dev/clotho-local
	pip install -e .
```

***You might need the root for this command***

#Installing PyLucene for better results

[Source](http://bendemott.blogspot.co.uk/2013/11/installing-pylucene-4-451.html)


##Install PyLucene

Download [pylucene](http://lucene.apache.org/pylucene/install.html)

Extract the Package:
```
tar -zxvf pylucene-4.5.1-src.tar.gz
```

##Dependencies

Install openjdk:

```
    sudo apt-get install openjdk-7-jdk
```

Install Apache Ant:

```
    sudo apt-get install ant
```

Install gnu c++ compiler:

```
    sudo apt-get install g++
```

Install python dev (python.h) headers:

```
    sudo apt-get install python-dev
```

Upgrade/install setuptools to 0.7 or higher:

```
    sudo apt-get install pip 

    pip install setuptools --upgrade 
```

Change to the jcc directory:

```
    cd pylucene-4.5.1-1/jcc  (edit to match your extracted directory)
```

Build and Install JCC:

```
    sudo python setup.py build

    sudo python setup.py install 
```

##Configure the build
If all that worked, you're ready to build pylucene!

```
    # cd up to the "pylucene-4.xxx" directory 

    cd .. 
```

Edit the file named "Makefile" located at the root of the pylucene-4.5.1 directory you just extracted

```
    # Locate this line

    # Linux     (Ubuntu 11.10 64-bit, Python 2.7.2, OpenJDK 1.7, setuptools 0.6.16)
```

Uncomment lines in the Makefile as shown (if you are on linux):

Issue make and install command:

```
    make 

    sudo make install  
```

##Test the installation:

```
    # open a python interpreter 

    python 

    # now at the prompt type... 

    import lucene 

    lucene.initVM()
```

 If no exceptions are raised you're done!  You've now installed PyLucene 4 !

 ##Import the data

 You need to copy the content of ``la`` folder in the folder ``texts/index``

 Then you need to update it to the 3.6.2 Version of Lucene 
