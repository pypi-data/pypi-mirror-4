# -*- coding: utf-8 -*-

try:
    from plone.app.blob.migrations import migrate
except ImportError:
    migrate = None

def migrateImagedEvent(context):
    if migrate is None:
        raise RuntimeError('You need plone.app.blob installed')
    return migrate(context, "Event", meta_type="ATEvent")
