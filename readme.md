#Clotho
This project is originally developed by Thibault Clerice. It is open source and so feel free to make pull request, report issues, fork...

This project aims to create network of occurences and auctoritas using Perseus data. 

##License and authorship
- The file `/morph/latin.morph.xml` is distributed with the Perseus Hopper source, which is (according only to the sourceforge project listing) licensed under the Mozilla Public License 1.1 (MPL 1.1)
- The file `/morph/stopwords.xml` comes fro http://wiki.digitalclassicist.org/Stopwords_for_Greek_and_Latin

##Installation for Ubuntu

Download the Perseus Hopper source code. Then, copy the file `sgml/xml/data/latin.morph.xml` in the folder `morph` of this programm.

From [Perseus databases dump](http://www.perseus.tufts.edu/hopper/opensource/download), download the following files :

	- [Chunks](http://www.perseus.tufts.edu/hopper/opensource/downloads/data/hib_chunks.tar.gz)
	- [Entities](http://www.perseus.tufts.edu/hopper/opensource/downloads/data/hib_entities.tar.gz)
	- [Entity Occurencies](http://www.perseus.tufts.edu/hopper/opensource/downloads/data/hib_entity_occurrences.tar.gz)
	- [Frequencies](http://www.perseus.tufts.edu/hopper/opensource/downloads/data/hib_frequencies.tar.gz)
	- [Lemmas](http://www.perseus.tufts.edu/hopper/opensource/downloads/data/hib_lemmas.tar.gz)
	- [Metadata](http://www.perseus.tufts.edu/hopper/opensource/downloads/data/metadata.tar.gz)

Download all the database files from Perseus in the same folder. Then in the terminal type :

```
for a in `ls -1 *.tar.gz`; do tar -xzOf $a | mysql --user=[User] --password=[Password] perseus2; done
```

From [Perseus download Page]() again, download the [processed texts](http://www.perseus.tufts.edu/hopper/opensource/downloads/data/sgml.xml.texts.tar.gz)