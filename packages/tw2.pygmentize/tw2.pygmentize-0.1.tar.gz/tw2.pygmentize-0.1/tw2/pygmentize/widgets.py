import tw2.core as twc

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


class Pygmentize(twc.Widget):
    template = "tw2.pygmentize.templates.pygmentize"

    name = twc.Param(default=property(lambda s: hasattr(s, 'compound_id') and s.compound_id or hasattr(s, 'id') and s.id or ''))

    lexer_name = twc.Param()
    lexer_args = twc.Param(default=dict())

    formatter_class = twc.Param(default=HtmlFormatter)
    style = twc.Param(default=u'default')
    noclasses = twc.Variable(default=True)
    formatter_args = twc.Param(default=dict())

    source = twc.Param()

    def prepare(self):
        super(Pygmentize, self).prepare()
        # put code here to run just before the widget is displayed
        lexer = get_lexer_by_name(self.lexer_name, **self.lexer_args)

        formatter_args = dict(self.formatter_args)
        if self.name:
            for k in 'lineanchors', 'linespans':
                if k in formatter_args:
                    formatter_args[k] = self.name + '_' + formatter_args[k]
        formatter = self.formatter_class(style=self.style, noclasses=self.noclasses,
            **formatter_args)

        self.source = highlight(self.source, lexer, formatter)
