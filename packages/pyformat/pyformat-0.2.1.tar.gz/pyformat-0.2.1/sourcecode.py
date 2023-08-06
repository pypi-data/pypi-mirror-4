from docutils import nodes
from docutils.parsers import rst
from docutils.parsers.rst import directives
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

city={
    'cpp':'c',
    'hypertext':'html'
}

pygments_formatter = HtmlFormatter(cssclass='code-block')

class CodeBlockDirective(rst.Directive):
    required_arguments=1
    has_content=True
    
    def __init__(self, name, arguments, options, content, lineno,
                       content_offset, block_text, state, state_machine):
        rst.Directive.__init__(self, name, arguments, options, content, lineno,
                       content_offset, block_text, state, state_machine)
    
    def run (self):
        lexer=None
        lname=self.arguments[0].lower()
        try:
            lexer = get_lexer_by_name(lname)
        except ValueError:
            pass
        # First try one of the SilverCity names, just in case
        try:
            lexer = get_lexer_by_name(city[lname])
        except KeyError:
            pass
        if not lexer:
            print "No lexer found for "+lname
            # no lexer found - use the text one instead of an exception
            lexer = get_lexer_by_name('text')
        parsed=highlight(u'\n'.join(self.content), lexer, pygments_formatter)
        node=nodes.raw('', parsed,format='html')
        node.in_rst='''\
.. code-block:: %s
%s
'''%(lname,'\n    '+('\n    ').join(self.content)+'\n')

        return [node]
        
directives.register_directive('sourcecode', CodeBlockDirective)
directives.register_directive('code-block', CodeBlockDirective)


if __name__ == "__main__":
    import docutils.core
    docutils.core.publish_cmdline(writer_name='html')
