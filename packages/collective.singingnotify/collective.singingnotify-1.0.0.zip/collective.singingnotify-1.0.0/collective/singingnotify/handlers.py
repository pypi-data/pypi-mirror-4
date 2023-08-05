from plone.app.contentrules.handlers import execute
from zope.app.component.hooks import getSite


def unsubscribed(event):
    """When an object is added, execute rules assigned to its new parent.

    There is special handling for Archetypes objects.
    """
    # The object added event executes too early for Archetypes objects.
    # We need to delay execution until we receive a subsequent IObjectInitializedEvent
    portal = getSite()
    execute(portal, event)