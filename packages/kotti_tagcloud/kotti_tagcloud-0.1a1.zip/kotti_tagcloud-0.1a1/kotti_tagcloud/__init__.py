from pyramid.i18n import TranslationStringFactory
_ = TranslationStringFactory('kotti_tagcloud')


def kotti_configure(settings):
    settings['pyramid.includes'] += ' kotti_tagcloud kotti_tagcloud.widget'
    settings['kotti.fanstatic.view_needed'] += '''\
        kotti_tagcloud.fanstatic.kotti_tagcloud'''
    settings['kotti.populators'] += ' kotti_tagcloud.populate.populate'


def includeme(config):
    config.add_translation_dirs('kotti_tagcloud:locale')
