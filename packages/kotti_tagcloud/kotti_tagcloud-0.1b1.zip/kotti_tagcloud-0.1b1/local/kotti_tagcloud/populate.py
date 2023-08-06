import colander

from kotti.views.slots import assign_slot

from kotti_settings.config import SlotSchemaNode
from kotti_settings.config import ShowInContextSchemaNode
from kotti_settings.util import add_settings
from kotti_settings.util import get_setting
from kotti_tagcloud import _


class TagcloudSchema(colander.MappingSchema):
    slot = SlotSchemaNode(colander.String())
    show_in_context = ShowInContextSchemaNode(colander.String())


TagcloudSettings = {
    'name': 'tagcloud_settings',
    'title': _(u'Tagcloud Settings'),
    'description': _(u"Settings for kotti_tagcloud"),
    'success_message': _(u"Successfully saved kotti_tagcloud settings."),
    'schema_factory': TagcloudSchema,
}


def populate():
    add_settings(TagcloudSettings)
    slot = get_setting('slot', u'left')
    assign_slot('tagcloud-widget', slot)
