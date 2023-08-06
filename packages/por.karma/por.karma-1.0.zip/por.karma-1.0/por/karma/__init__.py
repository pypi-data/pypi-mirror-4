import requests
from formalchemy import fields
from formalchemy import helpers as h

def includeme(config):
    import por.karma.models; por.karma.models
    import por.karma.events; por.karma.events

    config.add_route('karmademo', '/karmademo.json')
    config.add_view('por.karma.karmademo', renderer='json', route_name='karmademo')
    config.scan('por.karma.events')


class KarmaRenderer(fields.TextFieldRenderer):

    def render(self, **kwargs):
        karma_url = self.request.registry.settings.get('karma.url')
        if not karma_url:
            return ''
        try:
            karma = requests.get(karma_url, timeout=4, verify=False)
        except requests.exceptions.RequestException:
            return ''
        if karma.status_code != 200:
            return ''
        L = [(k['Titolo'], k['Id']) for k in karma.json()]
        return h.select(self.name, self.value, L, class_='i-can-haz-chzn-select', **kwargs) + \
               h.literal("<script>$('#%s').chosen()</script>" % self.name)


def karmademo(request):
    return [{"Id":1,"ExternalId":0,"Titolo":"Progetto1"},
            {"Id":2,"ExternalId":0,"Titolo":"Progetto2"},
            {"Id":3,"ExternalId":0,"Titolo":"Progetto3"}]
