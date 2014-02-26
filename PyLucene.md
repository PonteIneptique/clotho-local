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