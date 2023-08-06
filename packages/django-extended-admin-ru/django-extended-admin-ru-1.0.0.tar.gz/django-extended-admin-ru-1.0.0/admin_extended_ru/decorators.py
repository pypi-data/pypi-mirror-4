#-*- coding: utf-8 -*-

import re

from django.conf import settings
from django.utils.text import capfirst
from pymorphy import get_morph

morph = get_morph(settings.PYMORPHY_DICTS['ru']['dir'])


def message_wrapper(func):
    def wrapper(self, request, message):
        gram_info = morph.get_graminfo(self.model._meta.verbose_name.upper())[0]
        if -1 != message.find(u'"'):
            # message about some action with a single element

            words = [w for w in re.split("( |\\\".*?\\\".*?)", message) if w.strip()]
            form = gram_info['info'][:gram_info['info'].find(',')]
            message = u' '.join(words[:2])
            for word in words[2:]:
                if not word.isdigit():
                    word = word.replace(".", "").upper()
                    try:
                        info = morph.get_graminfo(word)[0]
                        if u'КР_ПРИЛ' != info['class']:
                            word = morph.inflect_ru(word, form).lower()
                        elif 0 <= info['info'].find(u'мр'):
                            word = morph.inflect_ru(word, form, u'КР_ПРИЧАСТИЕ').lower()
                        else:
                            word = word.lower()
                    except IndexError:
                        word = word.lower()
                message += u' ' + word
        else:
            # message about some action with a group of elements

            num = int(re.search(r'\d', message).group(0))
            words = message.split(u' ')
            message = words[0]
            pos = gram_info['info'].find(',')
            form = gram_info['info'][:pos] + u',' + u'ед' if 1 == num else u'мн'
            for word in words[1:]:
                if not word.isdigit():
                    word = word.replace(".", "").upper()
                    info = morph.get_graminfo(word)[0]
                    if u'КР_ПРИЛ' != info['class']:
                        word = morph.pluralize_inflected_ru(word, num).lower()
                    else:
                        word = morph.inflect_ru(word, form, u'КР_ПРИЧАСТИЕ').lower()
                message += u' ' + word

        message += '.'
        return func(self, request, capfirst(message))
    return wrapper
