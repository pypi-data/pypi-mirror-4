from pyramid.view import view_config
from kotti_settings.util import get_setting


@view_config(name='contentpreview_settings',
             permission='edit',
             renderer='json')
def contentpreview_settings(context, request):
    return {'view_name': get_setting('view_name'),
            'window_size': get_setting('window_size'),
            'delay_show': get_setting('delay_show'),
            'delay_hide': get_setting('delay_hide')}
