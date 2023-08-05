from time import time

from code import interact
from prody.atomic.select import FUNCTION_MAP
import pyparsing as  pp 

DEBUG=1

def foo(sel, loc, tokens, *args):
    if DEBUG == 0:
        return
    print '>>>', args[0]
    print sel
    print ' ' * (loc-1) + '^'
    print tokens
    print '\n'
    #interact(local=locals())

shortlist = pp.alphanums + '''~@#$.:;_','''
longlist = pp.alphanums + '''~!@#$%^&*()-_=+[{}]\|;:,<>./?()' '''

specialchars = pp.Group(pp.Literal('`') + 
                        pp.Optional(pp.Word(longlist + '"')) + 
                        pp.Literal('`'))
def specialCharsParseAction(token):
    if len(token[0]) == 2: # meaning `` was used
        return '_'
    else:
        return token[0][1]
specialchars.setParseAction(specialCharsParseAction)
regularexp = pp.Group(pp.Literal('"') + 
                      pp.Optional(pp.Word(longlist + '`')) + 
                      pp.Literal('"'))
def regularExpParseAction(sel, loc, token): 
    token = token[0]
    if len(token) == 2:
        return RE.compile('^()$')
    else:
        try:
            regexp = RE.compile(token[1])
        except:
            raise SelectionError(sel, loc, 'failed to compile regular '
                            'expression {0:s}'.format(repr(token[1])))
        else:
            return regexp
regularexp.setParseAction(regularExpParseAction)
oneormore = pp.OneOrMore(pp.Word(shortlist) | regularexp | 
                         specialchars)
funcnames = FUNCTION_MAP.keys()
functions = pp.Keyword(funcnames[0])
for func in funcnames[1:]:
    functions = functions | pp.Keyword(func)

parser = pp.operatorPrecedence(
     oneormore,
     [(functions, 1, pp.opAssoc.RIGHT,  lambda *args: foo(*(args + ('func',)))),
      (pp.oneOf('+ -'), 1, pp.opAssoc.RIGHT, lambda *args: foo(*(args + ('sign',)))),
      (pp.oneOf('** ^'), 2, pp.opAssoc.LEFT, lambda *args: foo(*(args + ('power',)))),
      (pp.oneOf('* / %'), 2, pp.opAssoc.LEFT, lambda *args: foo(*(args + ('mul',)))),
      (pp.oneOf('+ -'), 2, pp.opAssoc.LEFT, lambda *args: foo(*(args + ('add',)))),
      (pp.oneOf('< > <= >= == = !='), 2, pp.opAssoc.LEFT, lambda *args: foo(*(args + ('compare',)))),
      (pp.Keyword('not') 
      # pp.Regex('(ex)?bonded to') |
      # pp.Regex('(ex)?bonded [0-9]+ to') |
      # pp.Regex('same [a-z]+ as') | 
      # pp.Regex('(ex)?within [0-9]+\.?[0-9]* of'), 
      ,          1, pp.opAssoc.RIGHT, foo),
      #(pp.Keyword('&&&'), 2, pp.opAssoc.LEFT, lambda *args: foo(*(args + ('and',)))),
      (pp.Optional(pp.Keyword('and')), 2, pp.opAssoc.LEFT, lambda *args: foo(*(args + ('and',)))),
      #(pp.Optional(pp.Keyword('&&&'), default='&&&'), 2, pp.opAssoc.LEFT, lambda *args: foo(*(args + ('and',)))),
      (pp.Keyword('or'), 2, pp.opAssoc.LEFT, lambda *args: foo(*(args + ('or',)))),]
    )
    
parser.setParseAction(lambda *args: foo(*(args + ('parseaction',))))
parser.leaveWhitespace()
parser.enablePackrat()
parse = lambda string: parser.parseString(string, parseAll=True).asList()

DEBUG=0

t=time();
parse('aaa bbb and - ccc or x + z and x (y)')
print time()-t
t=time();
parse('aaa bbb and - ccc or x + z and x (y)')
print time()-t
t=time();
parse('aaa bbb and - ccc or x + z and x y')
print time()-t
t=time();
parse('aaa bbb and - ccc or x + z and x y')
print time()-t


DEBUG=1
