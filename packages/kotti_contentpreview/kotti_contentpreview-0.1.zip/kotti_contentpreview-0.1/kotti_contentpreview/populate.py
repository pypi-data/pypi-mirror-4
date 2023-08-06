from kotti_settings.util import add_settings
from kotti_contentpreview import _


contenpreview_settings = {
    'name': 'contentpreview_settings',
    'title': _(u'Contentpreview settings'),
    'success_message': _(u'Successfully saved kotti_contentpreview settings.'),
    'settings': [
        {'type': 'String',
         'name': 'view_name',
         'title': _(u'View name'),
         'description': _(u'The name of the view that should be used '
                          u'to preview the content.'),
         'default': '@@view', },
        {'type': 'String',
         'name': 'window_size',
         'title': _(u'Window size'),
         'description': _(u'Use any css compatible value to set the '
                          u'size of the window.'),
         'default': '50%', },
        {'type': 'Integer',
         'name': 'delay_show',
         'title': _(u'Delay show'),
         'description': _(u'The delay to show the popup window in '
                          u'milliseconds.'),
         'default': '500', },
        {'type': 'Integer',
         'name': 'delay_hide',
         'title': _(u'Delay hide'),
         'description': _(u'The delay to hide the popup window in '
                          u'milliseconds.'),
         'default': '750', },
    ]}


def populate():
    add_settings(contenpreview_settings)
