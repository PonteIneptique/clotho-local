#Arachne
This project is orinally developed by Thibault Clerice but it is open source and so feel free to make pull request, report issues, fork...

This project aims to create network of occurences and auctoritas using Perseus data. 

##Installation for Ubuntu

Download all the database files from Perseus in the same folder. Then in the terminal type :

```
for a in `ls -1 *.tar.gz`; do tar -xzOf $a | mysql --user=[User] --password=[Password] perseus2; done
```