import json
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class EmbedJS(BrowserView):

    template = ViewPageTemplateFile("embed.js.pt")

    def __call__(self):
        js = self.template() % {'context_url': self.context.absolute_url()}
        self.request.RESPONSE.setHeader('Content-Type', 'application/x-javascript; charset=utf-8')
        return js


class EmbedJSON(BrowserView):

    template = ViewPageTemplateFile("items_macro.pt")

    def __call__(self):
        self.request.RESPONSE.setHeader('Content-Type', 'application/x-javascript; charset=utf-8')
        params = self.request.form

        elements_length = json.loads(params.get('items','5'))
        new_window = json.loads(params.get('new_window','false'))
        html = self.render(elements_length, new_window)

        jsonp = "%(callback)s ( {'html': '%(html)s' } )"
        return jsonp % {'callback': params.get('callback'),
                        'html': html}

    def render(self, elements_length, new_window):
        items = self.context.queryCatalog()[:elements_length]
        html = self.template(items=items, new_window=new_window)
        html = html.replace('\n','').replace('"','\"')
        return html
