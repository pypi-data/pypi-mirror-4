"""Parsing module to parse a simple grammar of boolean operations, such as 
a>1
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
((a==b) & (c>1)) | (d<=2) | ((e>=1.5) & (g==0) & ! h)
"""

from pyparsing import *

class EvaluateNumber(object):
    """Class to evaluate a number by converting it into a float"""
    def __init__(self, tokens):
        self.value = tokens[0]
    def eval(self):
        return float(self.value)
    def __str__(self):
        return str(float(self.value))

class EvaluateVariable(object):
    """Class to evaluate a variable by calling the 'get' function"""
    def __init__(self, tokens):
        self.value = tokens[0]
    def eval(self):
        return get(self.value)
    def __str__(self):
        return str(self.value)

def opPair(tokenlist):
    """Given a list of tokens, returns pairs of tokens to the caller as a generator"""
    it = iter(tokenlist)
    while 1:
        try:
            yield(it.next(), it.next())
        except StopIteration:
            break

class EvaluateComparison(object):
    """Class to define the comparison operators. When eval is called the input is list is
    passed to the opPair generator and each pair is evaluated"""
    operators = {
        "<" :  ["lessthan",lambda a,b : a < b],
        ">" :  ["greaterthan",lambda a,b : a > b],
        ">=" : ["greaterequals",lambda a,b : a >= b],
        "<=" : ["lessequals",lambda a,b : a <= b],
        "==" : ["equals",lambda a,b : a == b],
        "!=" : ["notequal",lambda a,b : a != b],
        }
    def __init__(self, tokens):
        self.value = tokens[0]
        #print map(str,self.value)
    
    def eval(self):
        val1 = self.value[0].eval()
        for op,val in opPair(self.value[1:]):
            fn = EvaluateComparison.operators[op][1]
            val2 = val.eval()
            val1 =  fn(val1,val2)
        return val1
    
    def __str__(self):
        return "({0} {1} {2})".format(  str(self.value[0]), 
                                    EvaluateComparison.operators[self.value[1]][0],
                                    str(self.value[2]))

class EvaluateOrAnd(object):
    """Special class to evaluate an AND or OR"""
    operators = {
        "&" : ["and",lambda a,b : a & b],
        "|" : ["or",lambda a,b : a | b],
        }
    def __init__(self, tokens):
        self.value = tokens[0]
    
    def eval(self):
        val1 = self.value[0].eval()
        for op,val in opPair(self.value[1:]):
            fn = EvaluateOrAnd.operators[op][1]
            val2 = val.eval()
            val1 = fn(val1,val2)
        return val1
    
    def __str__(self):
        string = "("
        val1 = str(self.value[0])
        for op,val in opPair(self.value[1:]):
            fn = EvaluateOrAnd.operators[op][0]
            val2 = val
            string = string + "{0}, {1}, {2}".format(val1, fn,val2)
        string = string + ")"
        return string

class EvaluateNot(object):
    """Class to evaluate not, which only takes one argument"""
    operators = {
        "!" : ["(not)",lambda a : not a]
        }
    
    def __init__(self, tokens):
        self.value = tokens[0]

    def eval(self):
        for op,val in opPair(self.value[0:]):
            fn = EvaluateNot.operators[op][1]
            val2=val.eval()
            val = fn(val2)
        return val

    def __str__(self):
        return " ".join([str(v) for v in self.value])


#parser definition
class BoolParser(object):
    def __init__(self, EvaluateVariableChild=None, EvaluateNumberChild=None):
        EvaluateVariableChild = EvaluateVariableChild or EvaluateVariable
        EvaluateNumberChild = EvaluateNumberChild or EvaluateNumber
        #what is a float number
        floatNumber = Regex(r'[-]?\d+(\.\d*)?([eE][-+]?\d+)?')
        #a variable is a combination of letters, numbers, and underscor
        variable = Word(alphanums + "_")
        #a sign is plus or minus
        signOp = oneOf('+ -')
        #an operand is a variable or a floating point number
        operand = floatNumber ^ variable
        #when a floatNumber is found, parse it with evaluate number
        floatNumber.setParseAction(EvaluateNumberChild)
        #when a variable is found, parse it with the EvaluateVariableChild or EvaluateVariable
        variable.setParseAction(EvaluateVariableChild)
        #comparisons include lt,le,gt,ge,eq,ne
        comparisonOp = oneOf("< <= > >= == !=")
        #negation of the boolean is !
        notOp = oneOf("!")
        #an expression is a either a comparison or a NOT operation (where NOT a is essentially (a == False))
        comparisonExpression = operatorPrecedence(operand,
            [
                (comparisonOp, 2, opAssoc.LEFT, EvaluateComparison),
                (notOp, 1, opAssoc.RIGHT, EvaluateNot),
            ])
        
        #boolean logic of AND or OR
        boolOp = oneOf("& |")
        
        #a bool expression contains a nested bool expression or a comparison, joined with a boolean operation
        boolExpression = Forward()
        boolPossible = boolExpression | comparisonExpression
        self.boolExpression = operatorPrecedence(boolPossible,
            [
            (boolOp, 2, opAssoc.RIGHT, EvaluateOrAnd),
            ])
        return

    def parseString(self,line):
        if len(line): 
            print self.boolExpression.parseString(line)[0]

    def parse(self,line):
        if len(line):
            data= self.boolExpression.parseString(line)[0]
            return data.eval()

        
