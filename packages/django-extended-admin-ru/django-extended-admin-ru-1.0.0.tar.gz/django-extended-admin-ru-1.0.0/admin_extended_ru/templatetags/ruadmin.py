#-*- coding: utf-8 -*-

from django import template
from django.conf import settings
from django.template.base import Token
from django.template.loader_tags import do_include
from django.utils.text import capfirst
from pymorphy import get_morph

register = template.Library()
morph = get_morph(settings.PYMORPHY_DICTS['ru']['dir'])


@register.filter
def plural_from_object(source, obj):
    len_ = len(obj[0])
    if len_ == 1:
        return source
    return morph.pluralize_inflected_ru(source.upper(), len_).lower()


@register.filter
def plural_from_object_with_num(source, obj):
    len_ = len(obj[0])
    if len_ == 1:
        return source
    return '%d %s' % (len_, morph.pluralize_inflected_ru(source.upper(), len_).lower())


@register.filter
def plural_by_length(source, length):
    if length == 1:
        return source
    return morph.pluralize_inflected_ru(source.upper(), length).lower()


@register.simple_tag
def extratrans(source, type_='app'):
    if type_ == 'caption':
        captions = {
            'title': u'Панель администрирования сайта',
            'branding': u'Администрирование',
            'home': u'Главная'
        }
        captions.update(getattr(settings, 'ADMIN_CAPTIONS', {}))
        return captions.get(source, source)
    elif type_ == 'app':
        trans = getattr(settings, 'VERBOSE_APPS_NAMES', {}).get(source.lower(), source)
        return capfirst(trans) if source.istitle() else trans
    return source


@register.tag('render_breadcrumbs')
def do_render_breadcrumbs(parser, token):
    include = 'include "admin/breadcrumbs.html" with app_label=%s'
    return do_include(parser, Token(token.token_type, include % token.split_contents()[1]))
