#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

#
# Parse mapfiles
#

import sys
import os
import ply.lex as lex
import ply.yacc as yacc
from inspect import getfile, currentframe
from pyutilib.misc import flatten
from pyutilib.ply import t_newline, t_ignore, t_COMMENT, _find_column, p_error, ply_init

reserved = {
    'literals' : 'LITERALS',
    'set' : 'SET',
    'param' : 'PARAM',
    'var' : 'VAR',
    'obj' : 'OBJ',
    'con' : 'CON',
    'in' : 'IN',
    'within' : 'WITHIN',
    'integers' : 'INTEGERS',
    'reals' : 'REALS',
    'dimen' : 'DIMEN',
    'cross' : 'CROSS',
}

# Token names
tokens = [
    "COMMA",
    "SEMICOLON",
    "LBRACKET",
    "RBRACKET",
    "POSITIVEINTEGER",
    "WORD",
] + list(reserved.values())


# Regular expression rules
t_COMMA     = r","
t_LBRACKET  = r"\["
t_RBRACKET  = r"\]"
t_SEMICOLON = r";"
def t_POSITIVEINTEGER(t):
    r'[1-9][0-9]*'
    return t
def t_WORD(t):
    r'[a-zA-Z_][a-zA-Z_0-9\.]*'
    t.type = reserved.get(t.value,'WORD')    # Check for reserved words
    return t
#t_NONWORD   = r"[^\.A-Za-z0-9,;=\(\)\[\] \n\t\r]+"

# Error handling rule
def t_error(t):                 #pragma:nocover
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

_parse_info = None
_add_temp_sets = False
_parsedata = None
debugging = False

##
## Yacc grammar
##
## NOTE: This grammar is not intended to reflect the semantics of AMPL.
## Instead, our goal is to extract info about how the sets, variables, etc are
## declared.
##

def p_expr(p):
    '''expr : statements
            | '''
    pass

def p_statements(p):
    '''statements : statement statements
                  | statement '''

def p_statement(p):
    '''statement : SET WORD WITHIN set DIMEN POSITIVEINTEGER SEMICOLON
                 | SET WORD LBRACKET index RBRACKET WITHIN set DIMEN POSITIVEINTEGER SEMICOLON
                 | PARAM WORD IN set SEMICOLON
                 | PARAM WORD LBRACKET index RBRACKET IN set SEMICOLON
                 | VAR WORD SEMICOLON
                 | VAR WORD LBRACKET index RBRACKET SEMICOLON
                 | OBJ WORD SEMICOLON
                 | OBJ WORD LBRACKET index RBRACKET SEMICOLON
                 | CON WORD SEMICOLON
                 | CON WORD LBRACKET index RBRACKET SEMICOLON
    '''
    global _parse_info
    global _add_temp_sets
    index=None
    try:
        if p[1] == "set":
            if len(p) > 8:
                index = flatten(p[4])
                while "," in index:
                    index.remove(",")
            if len(p) == 8:
                _parse_info.add_symbol("set", p[2], superset=p[4], dimen=p[6], tmpsets=_add_temp_sets)
            else:
                _parse_info.add_symbol("set", p[2], superset=p[7], index=index, dimen=p[9], tmpsets=_add_temp_sets)
        else:
            if len(p) > 5:
                index = flatten(p[4])
                while "," in index:
                    index.remove(",")
            if p[1] == "param":
                if len(p) == 6:
                    _parse_info.add_symbol("param",p[2],superset=p[4])
                else:
                    _parse_info.add_symbol("param",p[2],index=index,superset=p[7])
            else:
                if len(p) == 4:
                    _parse_info.add_symbol(p[1],p[2])
                else:
                    _parse_info.add_symbol(p[1],p[2],index=index)
    except IOError:
        err = sys.exc_info()[1]
        print(err)
        p_error(p.lexer.token())
        raise yacc.SyntaxError          #pragma:nocover
    if debugging:           #pragma:nocover
        print("* DECL %s %s" % (str(p[1:]),str(index)))

def p_index(p):
    '''index : token
             | token COMMA index'''
    if len(p) == 2:
        p[0]=p[1:]
    else:
        p[0] = [p[1],p[2],p[3]]
    if debugging:           #pragma:nocover
        print("* INDEX %s %s" % (p[0],str(p[1:])))

def p_set(p):
    ''' set : WORD
            | LITERALS
            | REALS
            | INTEGERS
            | WORD CROSS set
            | LITERALS CROSS set
            | REALS CROSS set
            | INTEGERS CROSS set
    '''
    if len(p) == 2:
        p[0]=p[1]
    else:
        if type(p[3]) is list:
            p[0]=[p[1]]+p[3]
        else:
            p[0]=[p[1],p[3]]

def p_token(p):
    '''token : WORD
             | INTEGERS'''
    p[0]=p[1]
    if debugging:           #pragma:nocover
        print("* TOKEN %s" % p[1])

#
# The function that performs the parsing
#
def parse_mapfile(info, data=None, filename=None, debug=0, outputdir=None, add_temp_sets=False):
    global debugging
    global _add_temp_sets

    tabmodule = "mapfile_parser_table"
    if outputdir is None:
        # Try and write this into the module source...
        outputdir = os.path.dirname(getfile( currentframe() ))
        # Ideally, we would pollute a per-user configuration directory
        # first -- something like ~/.coopr.
        if not os.access(outputdir, os.W_OK):
            outputdir = os.getcwd()

    #
    # Always remove the parser.out file, which is generated to create debugging
    #
    if os.path.exists("parser.out"):        #pragma:nocover
        os.remove("parser.out")
    if debug > 0:                           #pragma:nocover
        #
        # Remove the parsetab.py* files.  These apparently need to be removed
        # to ensure the creation of a parser.out file.
        #
        if os.path.exists(tabmodule+".py"):
            os.remove(tabmodule+".py")
        if os.path.exists(tabmodule+".pyc"):
            os.remove(tabmodule+".pyc")
        debugging=True
    #
    # Build lexer
    #
    _lexer = lex.lex()
    #
    # Initialize parse object
    #
    global _parse_info
    _parse_info = info
    _add_temp_sets = add_temp_sets
    #
    # Build yaccer
    #
    _yaccer = yacc.yacc(debug=debug, tabmodule=tabmodule, outputdir=outputdir)
    #
    # Parse the file
    #
    global _parsedata
    if not data is None:
        _parsedata=data
        ply_init(data)
        yacc.parse(data, lexer=_lexer, debug=debug)
    elif not filename is None:
        f = open(filename)
        data = f.read()
        f.close()
        _parsedata=data
        ply_init(data)
        yacc.parse(data, lexer=_lexer, debug=debug)
    else:
        _parse_info = None
    debugging=False
    return _parse_info
