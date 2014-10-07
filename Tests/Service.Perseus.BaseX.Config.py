import sys

sys.path.append("../..")

from Services.Perseus.BaseX import *

C = Config()
print C.check()
C.install()