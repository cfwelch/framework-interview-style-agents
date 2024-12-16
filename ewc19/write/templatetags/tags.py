
from django import template

register = template.Library()

@register.filter(name='format_user')
def format_user(value):
    rv = value.replace(',', ' ')
    rv = [i[0].upper() + i[1:] for i in rv.split(' ')]
    return ' '.join(rv)

@register.filter(name='format_topic')
def format_topic(s):
    rtv = s[0] + s[1:].lower()
    if s == 'MONEY':
        rtv = 'Finance'
    elif s == 'FRIEND':
        rtv = 'Friends'
    elif s == 'POLITICAL':
        rtv = 'Politics'
    return rtv
