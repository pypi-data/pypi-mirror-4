from pyramid.events import subscriber
from pyramid.view import view_config

from kotti.resources import Tag
from kotti.views.slots import assign_slot
from kotti.views.slots import objectevent_listeners
from kotti.views.slots import slot_events

from kotti_settings.events import SettingsAfterSave
from kotti_settings.util import get_setting

from kotti_tagcloud.populate import choices


@view_config(name='tagcloud-widget',
             renderer='kotti_tagcloud:templates/tagcloud.pt')
def tagcloud_widget(context, request):
    tags = Tag.query.all()
    return {'tags': tags}


@subscriber(SettingsAfterSave)
def set_assigned_slot(event):
    """Reset the widget to the choosen slot."""

    # Check if the settings for this module was saved.
    if not event.module == __package__:
        return

    slot = get_setting('slot', u'left')
    slot_names = [name[0] for name in choices]

    # This is somewhat awkward. We check all slots if the widget is already
    # set and remove it from the listener before we set it to another one.
    for slot_event in slot_events:
        if slot_event.name not in slot_names:
            continue
        try:
            listener = objectevent_listeners[(slot_event, None)]
        except TypeError:
            listener = None
        if listener is not None:
            for func in listener:
                if func.func_closure[1].cell_contents == 'tagcloud-widget':
                    listener.remove(func)
    assign_slot('tagcloud-widget', slot)


def includeme(config):
    config.scan(__name__)
    config.add_translation_dirs('kotti_tagcloud:locale')
