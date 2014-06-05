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
	python setup.py
```