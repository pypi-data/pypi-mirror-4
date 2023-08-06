#
# New BSD License
# ---------------
# 
# Copyright (c) 2012, Kay-Uwe (Kiwi) Lorenz
# 
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# 
# * Neither the name of "Kay-Uwe (Kiwi) Lorenz" nor the
#   names of its contributors may be used to endorse or promote products
#   derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL "Kay-Uwe (Kiwi) Lorenz" BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
"""pygments lexer extension for aPTK grammars

:copyright: Copyright 2012 by Kay-Uwe (Kiwi) Lorenz
:license: New BSD License

This is a plugin for pygments to highlight aPTK grammars.  It is intended 
to be used for your Sphinx documentation. All you have to do is::

    import aptk.pygments_lexer

in your :file:`conf.py`.
"""

import re, sys
from pygments.lexer import ExtendedRegexLexer, LexerContext, bygroups
from pygments.token import Error, Text, Other, Comment, Operator, Keyword, \
     Name, String, Number, Generic, Punctuation

__all__ = ['APTKGrammarLexer']

class APTKGrammarLexer(ExtendedRegexLexer):
    """
    For aPTK grammar.
    """

    name = "aPTK grammar"

    aliases = ['aptk']
    filenames = ['*.aptk']
    mimetypes = ['text/x-aptk-grammar']
    flags = re.DOTALL | re.MULTILINE

    def rule_callback(self, match, ctx):
        #import rpdb2 ; rpdb2.start_embedded_debugger('foo')
        yield match.start(1), Text,          match.group(1) # whitespace
        yield match.start(2), Name.Function, match.group(2) # rule name
        yield match.start(3), Text,          match.group(3) # whitespace
        yield match.start(4), Keyword,       match.group(4) # operator

        # now process rule
        nctx = LexerContext(match.group(5), 0, ['root'])
        for i, t, v in self.get_tokens_unprocessed(context=nctx):
            yield match.start(3)+i, t, v
        ctx.pos = match.end()

    tokens = {
        'root': [
            (r'^(\s*)(<?[^:\s>]+>?)(\s+)([^=]*?=>?)((?=\s)[^\n]*(?:\n\1(?=\s)[^\n]*)*)', 
             rule_callback),
 #           (r'(?=[^\s])', 'rule'), #
 #           ],
 #       'rule': [
            #(r'^(\s*)(:grammar)(\s+)([\w\.\-]+)(?:(\s+)(extends[^\n]*(?:\n\1(?=\s)[^\n]*)*)', bygroups(Text, Keyword, Text, String)),
            (r'^(\s*)(:grammar)(\s+)([\w\-\.]+)(\s+)(extends)(\s+)([^\n]*(?:\n\1(?=\s)[^\n]+)*)', 
             bygroups(Text, Keyword, Text, Name.Class, Text, Keyword, Text, String)),
            (r'^(\s*)(:[\w-]+)(\s+)([^\n]*(?:\n\1(?=\s)[^\n]*)*)', bygroups(Text, Keyword, Text, String)),
            (r'\s+', Text),
            (r"(?<=\s)\|(?=\s)", Keyword),
            (r"(?<=[>\]])[?*+]", Keyword),
            (r'(<\.?)([^:\s>]+)(>)', 
             bygroups(Operator, Name.Function, Operator)),
            (r'(<)([^:\s>]+)(:)([^>]+)(>)',
             bygroups(Operator, Name.Function, Operator, String, Operator)),
            (r'(<)([^:\s>]+)(\{)((?:(?!\s\}>).)*\s)(\}>)(?=\s)',
             bygroups(Operator, Name.Function, Operator, String, Operator)),
            (r'[^\s]+', String), # here we could highlight included tokens or ctx references
            ],
    }

def register():
    import pygments.lexers._mapping as lexmap
    L = APTKGrammarLexer
    lexmap.LEXERS['APTKGrammarLexer'] = (
        'aptk.pygments_lexer', L.name, tuple(L.aliases), tuple(L.filenames),
        tuple(L.mimetypes))
    import pygments.lexers
    if 'APTKGrammarLexer' not in pygments.lexers.__all__:
        pygments.lexers.__all__.append('APTKGrammarLexer')

register()
