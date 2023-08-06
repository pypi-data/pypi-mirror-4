from pyramid.events import subscriber
from pyramid_formalchemy import events

from por.dashboard.events import AfterEntryCreatedEvent
from por.models.dashboard import Project
from por.karma import KarmaRenderer


#Project rendering events
@events.subscriber([Project, events.IBeforeRenderEvent])
def before_project_render(context, event):
    fs = event.kwargs['fs']
    if not fs._render_fields.keys():
        fs.configure(readonly=fs.readonly)
    fs.karma_id.set(renderer=KarmaRenderer)


@subscriber(AfterEntryCreatedEvent)
def after_search_query_created(event):
    if event.timeentry.project.karma_id:
        event.entry['karma'] = event.timeentry.project.karma_id
