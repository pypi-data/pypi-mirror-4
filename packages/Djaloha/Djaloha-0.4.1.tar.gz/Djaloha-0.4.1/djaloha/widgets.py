# -*- coding: utf-8 -*-

from floppyforms.widgets import TextInput
from django.utils.encoding import force_unicode
from django.forms import Media
from django.core.urlresolvers import reverse
from django.conf import settings

class AlohaInput(TextInput):
    """
    Text widget with aloha html editor
    requires floppyforms to be installed
    """

    template_name='djaloha/alohainput.html'

    def __init__(self, *args, **kwargs):
        kwargs.pop('text_color_plugin', None) # for compatibility with previous versions
        self.aloha_plugins = kwargs.pop('aloha_plugins', None)
        self.extra_aloha_plugins = kwargs.pop('extra_aloha_plugins', None)
        self.aloha_init_url = kwargs.pop('aloha_init_url', None)
        super(AlohaInput, self).__init__(*args, **kwargs)

    def _get_media(self):
        """
        return code for inserting required js and css files
        need aloha , plugins and initialization
        include the 3rd party ImagePlugin from tapo: make possible to drag-and-drop and edit images
        """

        try:
            custom_jquery = getattr(settings, 'DJALOHA_JQUERY', "js/jquery-1.7.1.min.js") # le fallback est celui de coop-cms ?
            aloha_init_url = self.aloha_init_url or getattr(settings, 'DJALOHA_INIT_URL', None) or reverse('aloha_init')

            aloha_plugins = self.aloha_plugins
            if not aloha_plugins:
                aloha_plugins = getattr(settings, 'DJALOHA_PLUGINS', None)
            if not aloha_plugins:
                aloha_plugins = (
                    "djaloha/format",
                    "common/highlighteditables",
                    "common/list",
                    "djaloha/link",
                    "common/undo",
                    "common/paste",
                    "common/commands",
                    "common/image",
                    "common/align",
                    "extra/attributes",
                    "common/characterpicker",
                    "djaloha/abbr",
                    "common/horizontalruler",
                    "common/table",
                )
            if self.extra_aloha_plugins:
                aloha_plugins = tuple(aloha_plugins) + tuple(self.extra_aloha_plugins)

            css = {
                'all': (
                    "aloha.0.20/css/aloha.css",
                )
            }

            js = (
                custom_jquery,
                # Yes I know this is very dirty but the better (less bad) solution so-far
                u'aloha.0.20/lib/aloha.js" data-aloha-plugins="{0}'.format(u",".join(aloha_plugins)),
                aloha_init_url,
            )

            return Media(css=css, js=js)
        except Exception, msg:
            print '## AlohaInput._get_media Error ', msg

    media = property(_get_media)
