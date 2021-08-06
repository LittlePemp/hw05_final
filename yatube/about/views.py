from django.views.generic.base import TemplateView


class AboutPage(TemplateView):
    template_name = 'author.html'


class AboutTechView(TemplateView):
    template_name = 'tech.html'
