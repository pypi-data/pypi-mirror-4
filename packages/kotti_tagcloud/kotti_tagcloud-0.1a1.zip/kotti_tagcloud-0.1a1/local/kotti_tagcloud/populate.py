import colander
import deform

from kotti.views.slots import assign_slot

from kotti_settings.util import add_settings
from kotti_settings.util import get_setting
from kotti_tagcloud import _


choices = (('left', _(u'left')),
           ('right', _(u'right')),
           ('abovecontent', _(u'abovecontent')),
           ('belowcontent', _(u'belowcontent')))


class SlotSchemaNode(colander.SchemaNode):
    name = 'slot'
    title = _(u'Direction')
    default = u'left'
    widget = deform.widget.SelectWidget(values=choices)


class TagcloudSchema(colander.MappingSchema):
    slot = SlotSchemaNode(colander.String())


TagcloudSettings = {
    'name': 'tagcloud_settings',
    'title': _(u'Tagcloud Settings'),
    'description': _(u"Settings for kotti_tagcloud"),
    'success_message': _(u"Successfully saved kotti_tagcloud settings."),
    'schema_factory': TagcloudSchema
}


def populate():
    add_settings(TagcloudSettings)
    slot = get_setting('slot', u'left')
    assign_slot('tagcloud-widget', slot)
