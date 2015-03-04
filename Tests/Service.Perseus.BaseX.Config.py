import sys

sys.path.append("../..")

from Services.Perseus.BaseX import *

C = Config()
#print C.check()
#C.install()

print C.search()
#http://www.perseus.tufts.edu/hopper/CTS?request=GetPassage&urn=urn:cts:latinLit:stoa0045.stoa004.perseus-lat1:1
#www.perseus.tufts.edu/hopper/CTS?request=GetPassage&urn=urn:cts:latinLit:stoa0162.stoa004.perseus-lat1:127.1@SAEPE[1]-Christi[1]