##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Engine
"""
from zope.interface import implementer
from zope.interface import provider
from zope.pagetemplate.interfaces import IPageTemplateEngine
from zope.pagetemplate.interfaces import IPageTemplateProgram

from z3c.pt.pagetemplate import PageTemplate as ChameleonPageTemplate
from chameleon.tal import RepeatDict


# Py3: Fix Chameleon's RepeatDict, which cannot be adapted. Sigh.
class TraversableRepeatDict(RepeatDict):
    __providedBy__ = None
    __provides__ = None

    def __conform__(self, iface):
        return None


@implementer(IPageTemplateProgram)
@provider(IPageTemplateEngine)
class Program(object):

    def __init__(self, template):
        self.template = template

    def __call__(self, context, macros, tal=True, **options):
        if tal is False:
            return self.template.body

        context.vars['repeat'] = TraversableRepeatDict(context.repeat_vars)

        return self.template.render(**context.vars)

    @classmethod
    def cook(cls, source_file, text, engine, content_type):
        template = ChameleonPageTemplate(
            text, filename=source_file, keep_body=True,
            )

        return cls(template), template.macros
