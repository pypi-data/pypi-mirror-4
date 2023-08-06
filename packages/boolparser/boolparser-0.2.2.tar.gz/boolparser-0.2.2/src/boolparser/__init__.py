
from boolparser.core import *

def test_parser():
    import sys
    test_string="""a>1
a<1
a>=1
a<=1
a<1 & (b>2 | c<2)
a==1 & b<-2
a==1 & ! b
(a==b)
(a==b) & (c>1)
((a==b) & (c>1)) | d<=2
(a==b) & (c>1) | d<=2 
(((a==b) & (c>1)) & (d<=2) & e>=1.5)
((a==b) & (c>1)) & (d<=2) & e>=1.5
((a==b) & (c>1)) | (d<=2) | ((e>=1.5) & (g==0) & ! h)((a==b) & (c>1)) | (d<=2) | ((e>=1.5) & (g==0) & ! h)
"""
    
    b = dict(a=4,b=5,c=6,d=7,e=8,f=9,g=10,h=False)
    class ev_dict(EvaluateVariable):
        def eval(self):
            #self.value is available
            return b.get(self.value,False)
        
    bp = BoolParser(ev_dict)
    if len(sys.argv)==1:
        for line in test_string.split("\n"):
            if line:
                print line, bp.parse(line)
    else:
        print "Parsing {0}".format(sys.argv[1])
        for line in open(sys.argv[1]):
            if line:
                print line
                bp.parseString(line)
