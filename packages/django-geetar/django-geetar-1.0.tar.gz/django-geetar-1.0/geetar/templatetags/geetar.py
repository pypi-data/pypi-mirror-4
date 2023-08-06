from math import floor
import re

from django import template
from django.conf import settings
from django.template.base import Node
from django.template.defaultfilters import stringfilter
from django.utils import simplejson
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils.text import Truncator


register = template.Library()


# ---- Filters


@register.filter
def even(value):
    return int(value) % 2 == 0


@register.filter
def odd(value):
    return not even(value)


@register.filter(is_safe=False)
@stringfilter
def split(value, character=','):

    """
    Simply calls built-in .split() method on the string, splitting it by the
    passed-in character

    Example

        list = 'Hey, there, dudes'
        {{ list|split:',' }} yields ['Hey', 'there', 'dudes']
    """

    return [bit.strip() for bit in value.split(character)]


@register.filter(is_safe=False)
@stringfilter
def possessive(value):

    """
    Possessive template filter. Takes a name and appends "'s" or "'" to the
    end depending on whether or not the name ends with an 's'

    Example:

        name = 'Sally'
        {{ name|possessive }} yields "Sally's"

        name = 'Chris'
        {{ name|possessive }} yields "Chris'"

    """

    return "%s'%s" % (value, '' if value.rstrip()[-1] == 's' else 's')


@register.filter
def jsonify(data):

    """
    Simple template tag proxy to simplejson.dumps()
    """

    return mark_safe(simplejson.dumps(data))


# Hella robbed from:
# http://www.holovaty.com/writing/django-two-phased-rendering/
# Adds {% raw %} / {% endraw %} template tag so you can throw in
# Django-template-like content that won't be parsed (e.g. Mustache)
#
# Copyright 2009, EveryBlock
# This code is released under the GPL.

@register.tag
def raw(parser, token):
    # Whatever is between {% raw %} and {% endraw %} will be preserved as
    # raw, unrendered template code.
    text = []
    parse_until = 'endraw'
    tag_mapping = {
        template.TOKEN_TEXT: ('', ''),
        template.TOKEN_VAR: ('{{', '}}'),
        template.TOKEN_BLOCK: ('{%', '%}'),
        template.TOKEN_COMMENT: ('{#', '#}'),
    }
    # By the time this template tag is called, the template system has already
    # lexed the template into tokens. Here, we loop over the tokens until
    # {% endraw %} and parse them to TextNodes. We have to add the start and
    # end bits (e.g. "{{" for variables) because those have already been
    # stripped off in a previous part of the template-parsing process.
    while parser.tokens:
        token = parser.next_token()
        if (token.token_type == template.TOKEN_BLOCK and token.contents == parse_until):
            return template.TextNode(u''.join(text))
        start, end = tag_mapping[token.token_type]
        text.append(u'%s%s%s' % (start, token.contents, end))
    parser.unclosed_block_tag(parse_until)


@register.filter(is_safe=False)
@stringfilter
def paragraphlist(value):

    """
    Takes a string and breaks it apart by newline/return characters and
    returns a list of paragraphs

    Example:

        'Hello there,

        My name is $horty'

        would yield:

        ['Hello there,', 'My name is $horty']

    """

    # Normalize newlines

    value = re.sub(r'[ \t]*(\r\n|\r|\n)[ \t]*', '\n', force_unicode(value.strip()))
    return re.split('\n{2,}', value)


@register.filter(is_safe=True)
def multibyte_truncate(value, arg):
    """
    Truncates (potentially multibyte) chunk of HTML after a certain number of words.

    Argument: A comma-separated string containing two numbers. The first is the
    number of words to truncate for utf-8 strings, the second for multibyte
    characters.

    Newlines in the HTML are preserved.
    """

    # workaround for the fact that filters can only take one arg
    args = [a.strip() for a in arg.split(',')]

    try:
        utf_length = int(args[0])
        multibyte_length = int(args[1])
    except ValueError: # invalid literal for int()
        return value # Fail silently.

    try:
        # this will fail for multibyte strings
        value.decode('utf-8')
    except UnicodeEncodeError:
        return Truncator(value).words(multibyte_length, html=True, truncate=' ...')

    return Truncator(value).words(utf_length, html=True, truncate=' ...')


# ---- Template Tags


class ColumnizeNode(Node):

    """
    Handle 'columnize' tag parsing
    """

    def __init__(self, expression, target, columns, stacked=False):

        """
        Columnize init

        `expression`    The FilterExpression instance for the source to
                        columnize from
        `target`        The target context variable for the resulting,
                        sorted/columnized data
        `columns`       The number of columns to sort the source data into
        `stacked`       Whether the data should be sorted in a stacked manner
                        or not. By default the data is sorted into columns by
                        alternating through the source, setting this to True
                        would break the contents of the source into columns,
                        maintaining its initial order.

        """

        self.expression = expression
        self.target = target
        self.columns = columns
        self.stacked = stacked

    def render(self, context):

        source_list = self.expression.resolve(context, True)

        if not source_list:
            context[self.target] = []
            return ''

        out = [[] for i in range(self.columns)]
        lengths = [0 for i in range(self.columns)]

        # Figure out how long each column should be

        if self.stacked:
            total = len(source_list)
            rem = total % self.columns

            if total > self.columns:
                lengths = [int(floor(float(total) / float(self.columns)))] * self.columns

            if rem:
                i = 0
                while rem:
                    lengths[i] += 1
                    rem -= 1
                    i += 1

        # Sort into columns

        i = 0
        column = 0

        for item in source_list:

            out[column].append(item)
            i += 1

            if self.stacked:
                if len(out[column]) == lengths[column]:
                    column += 1
            else:
                column = i % self.columns

        context[self.target] = out

        return ''


@register.tag(name='columnize')
def do_columnize(parser, token):

    """
    Take an iterable and sort the contents into the specified number of
    columns/buckets. By default, the contents are sorted by alternating
    columns, but the 'stacked' keyword can be used to break the contents into
    columns in the order that they appear in the iterable. So for example, the
    default behavior would look like this:

        mylist = [1, 2, 3, 4, 5]

        {% columnize mylist into 3 %}
        ...
        mylist = [[1, 4], [2, 5], [3]]

    Using the 'stacked' keyword looks like this:

        mylist = [1, 2, 3, 4, 5]

        {% columnize mylist into 3 stacked %}
        ...
        mylist = [[1, 2], [3, 4], [5]]

    Usage:

        Separate the contents of 'some_var' into 3 columns:

        {% columnize some_var into 3 %}

        Separate the contents of 'my_var' into 4 columns and store as
        'columnated':

        {% columnize my_var into 4 as columnated %}

        Separate the contents of 'rad_var' into 5 columns in its original
        order (stacked):

        {% columnize rad_var into 5 stacked %}

        Separate the contents of 'yay_var' into 8 columns in its original
        order (stacked) and store as 'yay_columns':

        {% columnize yay_var into 8 stacked as yay_columns %}

    """

    bits = token.contents.split()
    bits.pop(0) # Pop off 'columnize' bit

    if len(bits) < 3:
        raise template.TemplateSyntaxError("'columnize' template tag takes at least 3 arguments")

    source = bits.pop(0) # Store first argument as the 'source' variable

    # Validate 'into #' portion

    if bits[0] != 'into':
        raise template.TemplateSyntaxError("The 2nd argument for 'columnize' must be 'into', followed by the number of columns you want to divide into")

    bits.pop(0)

    try:
        columns = int(bits.pop(0))
    except:
        raise template.TemplateSyntaxError("The 3rd argument for 'columnize' must be numeric, indicating how many columns you want your variable divied into")

    # Validate optional 'stacked' keyword

    stacked = False

    if bits and bits[0] == 'stacked':
        stacked = True
        bits.pop(0)

    if bits:
        if len(bits) == 2 and bits[-2] == 'as':
            target = bits[-1]
        else:
            raise template.TemplateSyntaxError("The last 2 arguments of 'columnize' must be empty, or 'as' followed by the variable name you want the resulting columnized data stored into")
    else:
        target = source

    # Compile source expresion

    expression = parser.compile_filter(source)

    return ColumnizeNode(expression, target, columns, stacked)


@register.tag
def value_from_settings(parser, token):

    """
    Get a value from the global settings. Useful for retrieving
    environment-specific settings directly from the template.

    Usage:
        {% value_from_settings BLOG_URL %}
    """

    try:
        tag_name, var = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
    return ValueFromSettings(var)


class ValueFromSettings(template.Node):

    def __init__(self, var):
        self.arg = template.Variable(var)

    def render(self, context):
        return settings.__getattr__(str(self.arg))
