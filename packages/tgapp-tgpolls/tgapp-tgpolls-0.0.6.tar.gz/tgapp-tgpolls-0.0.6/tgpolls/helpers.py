# -*- coding: utf-8 -*-

"""WebHelpers used in tgapp-tgpolls."""

from webhelpers import date, feedgenerator, html, number, misc, text

def bold(text):
    return html.literal('<strong>%s</strong>' % text)

def radio_answer(name, value, text):
    return html.literal('<input name="radio_answer_%s" type="radio" value="%s">%s</input>' % (name, value, text))
