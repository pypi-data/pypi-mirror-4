from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('kotti_contentpreview')


def kotti_configure(settings):
    settings['pyramid.includes'] += ' kotti_contentpreview'
    settings['kotti.populators'] += ' kotti_contentpreview.populate.populate'


def includeme(config):

    config.add_translation_dirs('kotti_contentpreview:locale')
    config.scan(__name__)
