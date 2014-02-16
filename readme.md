#Arachne
This project is originally developed by Thibault Clerice. It is open source and so feel free to make pull request, report issues, fork...

This project aims to create network of occurences and auctoritas using Perseus data. 

##License and authorship
- The file `/morph/latin.morph.xml` is distributed with the Perseus Hopper source, which is (according only to the sourceforge project listing) licensed under the Mozilla Public License 1.1 (MPL 1.1)
- The file `/morph/stopwords.xml` comes fro http://wiki.digitalclassicist.org/Stopwords_for_Greek_and_Latin

##Installation for Ubuntu

Download all the database files from Perseus in the same folder. Then in the terminal type :

```
for a in `ls -1 *.tar.gz`; do tar -xzOf $a | mysql --user=[User] --password=[Password] perseus2; done
```
