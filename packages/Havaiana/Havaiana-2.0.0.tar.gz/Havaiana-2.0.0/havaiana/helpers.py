import os

from inspect import getmembers
from ojota import Ojota
from wtforms import Form, TextField, SelectField

import ojota.sources


def get_ojota_children(package):
    hijos = []
    items = getmembers(package)
    for item in items:
        try:
            if item[0] != "Ojota" and issubclass(item[1], Ojota):
                hijos.append(item)
        except TypeError:
            pass
    return hijos

def get_data_codes():
    path = ojota.sources._DATA_SOURCE
    dirs = [dir_ for dir_ in os.listdir(path)
            if os.path.isdir(os.path.join(path, dir_))]
    return ['Root'] + sorted(dirs)

def get_form(cls, form_data, update=False):
    class HavaianaForm(Form):
        pass
    fields = [cls.pk_field]
    if cls.required_fields is not None:
        fields = set(fields + list(cls.required_fields))
    for field in fields:
        text_field = TextField()
        setattr(HavaianaForm, field, text_field)
    for key, value in cls.relations.items():
        choices = [(obj.primary_key, str(obj)) for obj in  value[0].all()]
        text = value[1].replace("_", "  ").capitalize()
        text_field = SelectField(text, choices=choices)
        setattr(HavaianaForm, key, text_field)
    if update:
        form = HavaianaForm(obj=form_data)
    else:
        form = HavaianaForm(form_data)
    return form
