# lextab.py. This file automatically created by PLY (version 3.4). Don't edit!
_tabversion   = '3.4'
_lextokens    = {'CODE_END_DIRECTIVE': 1, 'TEXT': 1, 'NEWLINE': 1, 'EQUALS': 1, 'AT_DIRECTIVE': 1, 'CLOSE_PROPERTY_LIST': 1, 'COMMA': 1, 'OPEN_PROPERTY_LIST': 1, 'DOC_DIRECTIVE': 1, 'CHUNK_REFERENCE': 1, 'CODE_DIRECTIVE': 1}
_lexreflags   = 0
_lexliterals  = ''
_lexstateinfo = {'INITIAL': 'inclusive'}
_lexstatere   = {'INITIAL': [('(?P<t_AT_DIRECTIVE>@@)|(?P<t_CHUNK_REFERENCE>[ \\t]*@<[^\\]\\n]+>[ \\t]*)|(?P<t_NEWLINE>\\n+)|(?P<t_TEXT>[^@\\[\\]=,\n]+)|(?P<t_CODE_DIRECTIVE>@code)|(?P<t_DOC_DIRECTIVE>@doc)|(?P<t_CODE_END_DIRECTIVE>@=)|(?P<t_OPEN_PROPERTY_LIST>\\[)|(?P<t_COMMA>,)|(?P<t_EQUALS>=)|(?P<t_CLOSE_PROPERTY_LIST>])', [None, ('t_AT_DIRECTIVE', 'AT_DIRECTIVE'), ('t_CHUNK_REFERENCE', 'CHUNK_REFERENCE'), ('t_NEWLINE', 'NEWLINE'), (None, 'TEXT'), (None, 'CODE_DIRECTIVE'), (None, 'DOC_DIRECTIVE'), (None, 'CODE_END_DIRECTIVE'), (None, 'OPEN_PROPERTY_LIST'), (None, 'COMMA'), (None, 'EQUALS'), (None, 'CLOSE_PROPERTY_LIST')])]}
_lexstateignore = {'INITIAL': ''}
_lexstateerrorf = {'INITIAL': 't_error'}
