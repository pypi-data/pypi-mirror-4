# -*- coding: utf-8 -*-
from social_tags.objects import RenderObject


AVAILABLE = {
    'opengraph': 'OpenGraph',
}

class OpenGraph(RenderObject):
    template = 'social_tags/networks/opengraph.html'

    def prepare_context(self, context):
        context['locales'] = [l for l in context['locales'] if l != context['locale']]
        return context