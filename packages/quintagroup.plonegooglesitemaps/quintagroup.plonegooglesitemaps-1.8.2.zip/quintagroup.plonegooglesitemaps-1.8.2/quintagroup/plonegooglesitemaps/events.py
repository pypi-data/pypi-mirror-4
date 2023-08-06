try:
    from Products.DCWorkflow.events import AfterTransitionEvent
    AfterTransitionEvent()
except ImportError:
    # Copy AfterTransitionEvent from Plone-3/Products.DCWorkflow.events
    from zope.interface import implements
    from zope.app.event.objectevent import ObjectEvent
    from quintagroup.plonegooglesitemaps.interfaces import ITransitionEvent, \
        IAfterTransitionEvent

    class TransitionEvent(ObjectEvent):
        implements(ITransitionEvent)

        def __init__(self, obj, workflow, old_state, new_state, transition,
                     status, kwargs):
            ObjectEvent.__init__(self, obj)
            self.workflow = workflow
            self.old_state = old_state
            self.new_state = new_state
            self.transition = transition
            self.status = status
            self.kwargs = kwargs

    class AfterTransitionEvent(TransitionEvent):
        implements(IAfterTransitionEvent)
