from django.views import generic as views

from . import models


class DetailView(views.DetailView):
    model = models.Series

    def get_template_names(self, **kwargs):
        return [
            'armstrong/apps/series/specific/%s.html' % self.object.slug,
            'armstrong/apps/series/series_detail.html',
        ]
