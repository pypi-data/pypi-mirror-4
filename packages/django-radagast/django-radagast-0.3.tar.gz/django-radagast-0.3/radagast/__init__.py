from django.views.generic.base import TemplateView
from django import http

import jingo

class Wizard(TemplateView):
    """A wrapper around the FormWizard in Django that makes a few changes.
    It renders different templates if the request is Ajax
    """
    template_name = 'templates/radagast/starts.html'

    def __call__(self, request, *args, **kw):
        raise NotImplementedError

    def get(self, request, step=''):
        raise NotImplementedError

    def post(self, request, step=''):
        raise NotImplementedError

    def get_context_data(self, *kw):
        return {}

    def get_step(self, step):
        if not step:
            return self.first_step
        if step in self.steps:
            return self.steps[step]
        raise http.Http404

    def render_template(self, request):
        """
        Will render the template if using Ajax. If not will wrap the
        template in self.wrapper and use that.
        """
        context = {}
        context.update(self.extra_context)
        if request.is_ajax():
            return jingo.render(request, self.get_template(step), context)
        else:
            wrapper = jingo.env.get_template(self.wrapper)
            source = jingo.render_to_string(request, self.get_template(step),
                                            context)
            context.update({'content': source})
            return jingo.render(request, wrapper, context)
