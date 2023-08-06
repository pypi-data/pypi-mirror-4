#!/home/yonatanf/.virtualenvs/survey/bin/python

'''
A simple script that uses that survey2 package.
Note that unless that correct python interpreter is previously activated
(e.g by running the mipython2.sh script), the first line must be identical to 
the one at the top of this file.
Additionaly, the survey2 package needs to be loaded before it can be used.   
'''

from survey2 import *

x = DF([[0.,1],[2,3],[4,5]], columns=['OTU1','OTU2'],index=['sample'+str(i) for i in xrange(3)])
print normalize(x)

