from django import template
from django.template import Context
from django.template.loader import get_template


register = template.Library()


@register.filter
def as_bootstrap(form):
    template = get_template('bootstrap_form/form.html')

    c = Context({
        'form': form
    })

    return template.render(c)


@register.filter
def klass(ob):
    return ob.__class__.__name__.lower()
