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
# TODOs
#
# Handle comment lines
# Print constraint names "subject to" instead of "subject" "to"
# Parse dimensions of sets, params, vars, etc...
#

import re
import os
import ply.lex as lex
import ply.yacc as yacc
from inspect import getfile, currentframe
from coopr.sucasa.ampl_info import AmplInfo
from pyutilib.misc import flatten
from pyutilib.ply import t_newline, t_ignore, _find_column, p_error, ply_init

_parse_info = None
_comment_list = []
_parsedata = None
debugging = False

reserved = {
    'check' : 'CHECK',
    'data' : 'DATA',
    'set' : 'SET',
    'param' : 'PARAM',
    'var' : 'VAR',
    'minimize' : 'MIN',
    'maximize' : 'MAX',
    'subject' : 'SUBJECT',
    's.t.' : 'ST',
    'to' : 'TO',
    'in' : 'IN',
    'within' : 'WITHIN',
    'sum' : 'SUM',
    'node' : 'NODE',
    'arc' : 'ARC',
    'dimen' : 'DIMEN',
    'integer' : 'INTEGER',
    'binary' : 'BINARY',
    'symbolic' : 'SYMBOLIC',
    'Integers' : 'INTEGERS',
    'Reals' : 'REALS'
}

# Token names
tokens = [
    "COMMA",
    "LBRACE",
    "RBRACE",
    "NUMBER",
    "SEMICOLON",
    "COLON",
    "COLONEQ",
    "LBRACKET",
    "RBRACKET",
    "LPAREN",
    "RPAREN",
    "LT",
    "GT",
    "LTEQ",
    "GTEQ",
    "LTLT",
    "GTGT",
    "LTGT",
    "RANGE",
    "WORD",
    "NONWORD",
] + list(reserved.values())

# Regular expression rules
t_COMMA     = r","
t_LBRACKET  = r"\["
t_RBRACKET  = r"\]"
t_NUMBER    = r"[0-9]+(\.[0-9]+){0,1}"
t_SEMICOLON = r";"
t_COLON     = r":"
t_COLONEQ   = r":="
t_LT        = r"<"
t_GT        = r">"
t_LTEQ      = r"<="
t_GTEQ      = r">="
t_LTLT      = r"<<"
t_GTGT      = r">>"
t_LTGT      = r"<>"
t_LBRACE    = r"{"
t_RBRACE    = r"}"
t_LPAREN    = r"\("
t_RPAREN    = r"\)"
t_RANGE     = r"\.\."

# Discard comments
def t_COMMENT(t):
    r'\#[^\n]*'
    global _comment_list
    _comment_list.append(t.value)

def process_comment_list():
    global _comment_list
    global _parse_info

    for comment in _comment_list:
        tmp = re.split('[ \t]+',comment.strip())
        if len(tmp) > 3 and tmp[1] == "SUCASA":
            if tmp[2] == "SYMBOLS:":
                _parse_info.exported_symbols = set(tmp[3:])
            else:
                _parse_info.add_mapfile_declaration(tmp[3]," ".join(tmp[2:]))
        if len(tmp) > 2 and tmp[0] == "#SUCASA":
            if tmp[1] == "SYMBOLS:":
                _parse_info.exported_symbols = set(tmp[2:])
            else:
                _parse_info.add_mapfile_declaration(tmp[2]," ".join(tmp[1:]))
    _comment_list = []

def t_WORD(t):
    r'[a-zA-Z_][a-zA-Z_0-9\.]*'
    t.type = reserved.get(t.value,'WORD')    # Check for reserved words
    return t
t_NONWORD   = r"[^\.A-Za-z0-9,;:<>\#{}\(\)\[\] \n\t\r]+"

# Error handling rule
def t_error(t):             #pragma:nocover
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

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
    process_comment_list()

def p_statements(p):
    '''statements : statement statements
                  | statement '''

def p_statement(p):
    '''statement : SET WORD SEMICOLON
                 | SET WORD csdecl SEMICOLON
                 | SET WORD WITHIN csdecl SEMICOLON
                 | SET WORD LBRACE index RBRACE SEMICOLON
                 | SET WORD LBRACE index RBRACE csdecl SEMICOLON
                 | SET WORD LBRACE index RBRACE WITHIN csdecl SEMICOLON
                 | PARAM  WORD SEMICOLON
                 | PARAM  WORD csdecl SEMICOLON
                 | PARAM  WORD LBRACE index RBRACE SEMICOLON
                 | PARAM  WORD LBRACE index RBRACE csdecl SEMICOLON
                 | VAR  WORD SEMICOLON
                 | VAR  WORD csdecl SEMICOLON
                 | VAR  WORD LBRACE index RBRACE SEMICOLON
                 | VAR  WORD LBRACE index RBRACE csdecl SEMICOLON
                 | CHECK COLON misc SEMICOLON
                 | CHECK LBRACE index RBRACE COLON misc SEMICOLON
                 | row WORD SEMICOLON
                 | row WORD csdecl SEMICOLON
                 | row WORD LBRACE index RBRACE SEMICOLON
                 | row WORD LBRACE index RBRACE csdecl SEMICOLON
                 | row WORD COLON WORD SEMICOLON
                 | row WORD COLON csdecl SEMICOLON
                 | row WORD LBRACE index RBRACE COLON WORD SEMICOLON
                 | row WORD LBRACE index RBRACE COLON csdecl SEMICOLON
                 | data
    '''
    global _parse_info
    index = []
    if len(p) > 5 and p[3] is '{':
        index = flatten(p[4])
        while "," in index:
            index.remove(",")

    if p[1] in ("set", "param", "var", "minimize", "maximize", "subject", "s.t."):
        dimen=1
        superset=None
        setlist = []
        if p[1] == "set":
            if len(p) == 5:
                setlist = p[3]
            elif len(p) == 6:
                setlist = p[4]
            elif len(p) == 8:
                setlist = p[6]
            elif len(p) == 9:
                setlist = p[7]
        elif p[1] == "param":
            if len(p) == 5:
                setlist = p[3]
            if len(p) == 8:
                setlist = p[6]

        tmp = flatten(setlist)
        setlist=[]
        for item in tmp:
            setlist = setlist + re.split('[\t ]+',item)

        if "integer" in setlist or "binary" in setlist or "Integers" in setlist:
            superset = "integers"
        elif "symbolic" in setlist:
            superset = "literals"
        elif "Reals" in setlist:
            superset = "reals"

        if p[1] == "param" and superset is None:
            superset="reals"

        #print "HERE X",p[1:],superset,len(p),setlist
        _parse_info.add(p[1],p[2], index, dimen=1, superset=superset)
    #
    # checks are not named, so we ignore them
    #
    elif p[1] in ("check", "arc", "node", "data"):
        process_comment_list()
        return
    else:                           #pragma:nocover
        #
        # If the AMPL model is syntactically correct, we should never see this
        #
        print("ERROR statement "+str(p[1:]))
    if debugging:                   #pragma:nocover
        if p[1] != "data":
            print("* DECL %s %s %s" % (p[1],p[2],index))
    process_comment_list()

def p_row(p):
    '''row : MIN
           | MAX
           | NODE
           | ARC
           | SUBJECT TO
           | ST'''
    p[0] = p[1]

def p_index(p):
    '''index : setname
             | token
             | misc
             | setname COMMA index
             | token COMMA index
             | misc COMMA index'''
    if len(p) == 2:
        tmp=p[1:]
    else:
        tmp = [p[1],p[2],p[3]]
    if debugging:                   #pragma:nocover
        print( "* INDEX %s %s" % (tmp,str(p[1:])))
    p[0] = tmp

def p_csdecl(p):
    '''csdecl : token
             | misc_bool
             | token COMMA csdecl
             | misc_bool COMMA csdecl'''
    if len(p) == 2:
        p[0]=p[1:]
    else:
        p[0] = flatten(p[1:])
        #if type(p[1]) is list:
            #p[0] = p[1] + [p[2],p[3]]
        #else:
            #p[0] = [p[1],p[2],p[3]]
    if debugging:                   #pragma:nocover
        print("* INDEX %s %s" % (p[0],str(p[1:])))

def p_setname(p):
    '''setname : token IN token Xmisc_bool
               | token IN misc Xmisc_bool'''
    p[0] = p[3]
    if debugging:                   #pragma:nocover
        print("* SETNAME %s" % p[0])

def p_misc(p):
    '''misc : token token_list'''
    p[0] = p[1]+" "+p[2]
    if debugging:                   #pragma:nocover
        print("* MISC %s" % p[0])

def p_token_list(p):
    '''token_list : token_list token
                  | token'''
    if len(p) > 2:
        p[0] = p[1]+" "+p[2]
    else:
        p[0] = p[1]
    if debugging:                   #pragma:nocover
        print( "* TOKENS %s %s" % (p[0],str(p[1:])))

def p_token(p):
    '''token : WORD
             | NUMBER
             | RANGE
             | INTEGER
             | BINARY
             | SYMBOLIC
             | REALS
             | INTEGERS
             | IN
             | TO
             | GT
             | LT
             | LTGT
             | GTEQ
             | LTEQ
             | DIMEN
             | COLONEQ
             | SUM
             | LBRACKET csdecl RBRACKET
             | LBRACE csdecl RBRACE
             | LPAREN csdecl RPAREN
             | LTLT csdecl SEMICOLON csdecl GTGT
             | NONWORD'''
    if len(p) == 2:
        p[0]=p[1]
    else:
        p[0] = " ".join(flatten(p[1:]))
    if debugging:                   #pragma:nocover
        print("* TOKEN %s %s" % (p[0],str(p[1:])))

def p_Xmisc_bool(p):
    '''Xmisc_bool : COLON misc_bool
                 | '''
    if len(p) > 1:
        p[0] = p[2]

def p_misc_bool(p):
    '''misc_bool : token bool_token_list'''
    p[0] = p[1]+" "+p[2]
    if debugging:                   #pragma:nocover
        print("* MISC_BOOL %s" % p[0])

def p_bool_token_list(p):
    '''bool_token_list : bool_token_list token
                  | bool_token_list COLON token
                  | COLON token
                  | bool_token_list IN token
                  | IN token
                  | token'''
    if len(p) > 2:
        p[0] = p[1]+" "+p[2]
    else:
        p[0] = p[1]
    if debugging:                   #pragma:nocover
        print("* BOOL_TOKENS %s %s" % (p[0],str(p[1:])))

def p_data(p):
    '''data : DATA SEMICOLON datalines
            | DATA SEMICOLON'''
    p[0] = 'data'

def p_datalines(p):
    '''datalines : dataline datalines
                 | dataline'''

def p_dataline(p):
    '''dataline : anytokens SEMICOLON'''

def p_anytokens(p):
    '''anytokens : anytoken anytokens
                 | anytoken'''

def p_anytoken(p):
    '''anytoken : WORD
             | SET
             | PARAM
             | NUMBER
             | IN
             | TO
             | GT
             | LT
             | GTEQ
             | LTEQ
             | COLON
             | COLONEQ
             | COMMA
             | LBRACE
             | RBRACE
             | LBRACKET
             | RBRACKET
             | LPAREN
             | RPAREN
             | RANGE
             | NONWORD'''

#
# The function that performs the parsing
#
def parse_ampl(data=None, filename=None, debug=0, outputdir=None):
    global debugging

    tabmodule = "ampl_parser_table"
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
    _parse_info = AmplInfo()
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
        ply_init(_parsedata)
        _yaccer.parse(data, lexer=_lexer, debug=debug)
    elif not filename is None:
        f = open(filename)
        data = f.read()
        f.close()
        _parsedata=data
        ply_init(_parsedata)
        _yaccer.parse(data, lexer=_lexer, debug=debug)
    else:
        _parse_info = None
    #
    # Disable parsing I/O
    #
    debugging=False
    return _parse_info
