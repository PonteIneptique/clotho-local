#Installation for Ubuntu

Download all the database files from Perseus in the same folder. Then in the terminal type :

```
for a in `ls -1 *.tar.gz`; do tar -xzOf $a | mysql --user=[User] --password=[Password] perseus2; done
```