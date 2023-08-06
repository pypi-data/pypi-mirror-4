import copy
from django import forms
from django import template
from django.template.loader import render_to_string
from django.utils.datastructures import SortedDict

register = template.Library()


@register.filter
def quick_form(form, template='djtools/quick_form.html'):
    return render_to_string(template, {'form': form})


'''
    Adapted from http://www.djangosnippets.org/snippets/1019/
    
    Example Usage:
    
    {% load djtools_form_tags %}
    <fieldset id="contact_details">
        <legend>Contact details</legend>
        <ul>
    {% get_fieldset first_name,last_name,email,cell_phone as personal_fields from form %}
    {{ personal_fields.as_ul }}
        </ul>
    </fieldset>

    <fieldset>
        <legend>Address details</legend>
        <ul>
    {% get_fieldset street_address,post_code,city as address_fields from form %}
    {{ address_fields.as_ul }}
        </ul>
    </fieldset>
'''
class FieldSetNode(template.Node):
    def __init__(self, fields, variable_name, form):
        self.fields = fields
        self.variable_name = variable_name
        self.form = form

    def render(self, context):
        form = template.Variable(self.form).resolve(context)
        new_form = copy.copy(form)
        new_form.fields = SortedDict([
            (key, value) \
                for key, value in form.fields.items() if key in self.fields
        ])

        context[self.variable_name] = new_form
        return u''


@register.tag
def get_fieldset(parser, token):
    try:
        name, fields, as_, variable_name, from_, form = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            'bad arguments for %r' % token.split_contents()[0]
        )

    return FieldSetNode(fields.split(','), variable_name, form)
