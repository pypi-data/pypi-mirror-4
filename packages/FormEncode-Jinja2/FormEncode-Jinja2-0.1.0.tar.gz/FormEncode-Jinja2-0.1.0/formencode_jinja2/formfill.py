import collections
import formencode.htmlfill
import jinja2
import jinja2.ext
from jinja2 import nodes


class FormFillExtension(jinja2.ext.Extension):
    """Jinja2 extension for filling HTML forms via :mod:`formencode.htmlfill`.

    For example, this code::

       {% formfill {'username': 'robert', 'email': 'robert153@usrobots.com'}
              with {'username': 'This name is invalid'} %}
       <form action="/register" method="POST">
           <input type="text" name="username" />
           <form:error name="username">
           <input type="password" name="password" />
           <input type="email" name="email" />
       </form>
       {% endformfill %}

    will be rendered like below::

       <form action="/register" method="POST">
           <input type="text" name="username" class="error" value="robert" />
           <span class="error-message">This name is invalid</span>
           <input type="password" name="password" value="" />
           <input type="email" name="email" value="robert153@usrobots.com" />
       </form>


    :param defaults: a dict-like object that contains default values of
                     the input field (including ``select`` and ``textarea``)
                     surrounded in the template tag.
                     Keys contain a value of ``name`` attribute of the input
                     field, and values contain its default value.
    :param errors: a dict-like object that contains messages for
                   the error of the input fields. this value will also effect
                   ``class`` attribute of the input field.
    :returns: rendered forms

    """
    tags = frozenset(['formfill'])

    def parse(self, parser):
        token = next(parser.stream)
        defaults = parser.parse_expression()
        if parser.stream.skip_if('name:with'):
            errors = parser.parse_expression()
        else:
            errors = nodes.Const({})
        if isinstance(defaults, nodes.Name):
            defaults = nodes.Getattr(nodes.ContextReference(),
                                     defaults.name, self.environment)
        if isinstance(errors, nodes.Name):
            errors = nodes.Getattr(nodes.ContextReference(),
                                   errors.name, self.environment)
        body = parser.parse_statements(['name:endformfill'], drop_needle=True)
        return nodes.CallBlock(
            self.call_method('_formfill_support', (defaults, errors)),
            (), (), body).set_lineno(token.lineno)

    def _formfill_support(self, defaults, errors, caller):
        if not isinstance(defaults, collections.Mapping):
            raise TypeError("argument 'defaults' should be "
                            "collections.Mapping, not {0!r}".format(defaults))
        if not isinstance(errors, collections.Mapping):
            raise TypeError("argument 'errors' should be collections.Mapping, "
                            "not {0!r}".format(errors))
        rv = caller()
        return formencode.htmlfill.render(
            rv, defaults, errors, error_formatters=self.ERROR_FORMATTERS)

    ERROR_FORMATTERS = {
        'default': lambda msg: '<span class="error-message">{0}</span>'
                               .format(msg),
    }
