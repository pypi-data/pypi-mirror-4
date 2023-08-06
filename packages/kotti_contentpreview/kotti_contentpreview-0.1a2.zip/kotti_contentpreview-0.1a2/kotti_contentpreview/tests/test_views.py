from kotti.resources import get_root
from kotti_contentpreview.views import contentpreview_settings


def test_settings_view(dummy_request, contentpreview_populate_settings):
    root = get_root()
    settings = contentpreview_settings(root, dummy_request)
    assert settings['view_name'] == u'@@view'
    assert settings['window_size'] == u'50%'
    assert settings['delay_show'] == u'500'
    assert settings['delay_hide'] == u'750'
