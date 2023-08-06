from pyramid.interfaces import ITranslationDirectories

from kotti_tagcloud import includeme
from kotti_tagcloud import kotti_configure


def test_kotti_configure():

    settings = {
        'pyramid.includes': '',
        'kotti.fanstatic.view_needed': '',
        'kotti.populators': '',
    }

    kotti_configure(settings)
    assert settings['pyramid.includes'] == \
        ' kotti_tagcloud kotti_tagcloud.widget'
    assert settings['kotti.fanstatic.view_needed'] == \
        '        kotti_tagcloud.fanstatic.kotti_tagcloud'
    assert settings['kotti.populators'] == ' kotti_tagcloud.populate.populate'


def test_includeme(config):

    includeme(config)

    utils = config.registry.__dict__['_utility_registrations']
    k = (ITranslationDirectories, u'')

    # test if the translation dir is registered
    assert k in utils
    assert utils[k][0][0].find('kotti_tagcloud/locale') > 0
