import os

from inspect import getmembers

import ojota.sources

from ojota import Ojota, current_data_code
from flask.helpers import send_file
from flask import Flask, render_template, redirect

from jinja2 import FileSystemLoader
template_path = os.path.join(os.path.dirname(__file__), "templates")

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

def default_renderer(field, item, backwards=False):
    if item.required_fields is not None:
        required = field in item.required_fields
    else:
        required = False
    value = getattr(item, field)
    relation_data = item.relations.get(field)

    if backwards:
        items = []
        for element in value:
            item_ = '<a href="/%s/%s">%s</a>' % (element.plural_name,
                                                element.primary_key,
                                                element)
            items.append(item_)
        value = ", ".join(items)
        related = False
    elif value is None or relation_data is None:
        related = False
    else:
        related = "/%s/%s" % (relation_data[0].plural_name, value)
        value = relation_data[0].get(value)
        field = relation_data[1]

    if field == item.pk_field:
        field = "Primary Key (%s)" % field
    else:
        field = field.replace("_", "  ").capitalize()

    return (field, value, required, related)

def render_field(field, item, renderers, backwards=False):
    render = default_renderer
    for renderer in renderers:
        if renderer[0] == field:
            render = renderer[1]

    return render(field, item, backwards)

def get_data_codes():
    path = ojota.sources._DATA_SOURCE
    dirs = [dir_ for dir_ in os.listdir(path)
            if os.path.isdir(os.path.join(path, dir_))]
    return ['Root'] + sorted(dirs)


def run(package, title="Havaiana", renderers=None):
    def default_data():
        data = {}

        data['title'] = title
        data['data_code'] = Ojota.CURRENT_DATA_CODE
        if data['data_code'] == "":
            data['data_code'] = "Root"
        data['data_codes'] = get_data_codes()
        return data

    if renderers is None:
        renderers  = []
    classes = get_ojota_children(package)
    app = Flask(__name__)
    app.jinja_loader = FileSystemLoader(template_path)

    classes_map = {}
    for item in classes:
        classes_map[item[1].plural_name] = item

    @app.route('/change-data-code/<data_code>')
    def change_data_code(data_code):
        if data_code == 'Root':
            data_code = ''
        current_data_code(data_code)
        return redirect('/')

    @app.route("/<name>")
    @app.route("/<name>/<pk>")
    def table(name, pk=None):
        data_dict = default_data()
        item = classes_map[name]
        cls = item[1]
        class_renderers = [renderer[1:] for renderer in renderers
                           if renderer[0] == item[0]]
        data_dict['class_name'] = name
        if pk is None:
            data_dict['items'] = cls.all()
            template = 'table.html'
        else:
            params = {getattr(cls, "pk_field"): pk}
            item = cls.get(**params)
            attrs = []
            for field in item.fields:
                attrs.append(render_field(field, item, class_renderers))
            for bw_rel in item.backwards_relations:
                attrs.append(render_field(bw_rel, item, class_renderers, True))

            data_dict['item'] = item
            data_dict['attrs'] = attrs
            template = 'item.html'
        return render_template(template, **data_dict)

    @app.route('/media/<path:filename>')
    def custom_static(filename):
        parts = filename.split("/")
        dir_name = "/".join(parts[:-1])
        filename = parts[-1]
        return send_file("templates/static/%s/%s" % (dir_name, filename))

    @app.route('/absolute//<path:filename>')
    def custom_absolute_static(filename):
        parts = filename.split("/")
        dir_name = "/".join(parts[:-1])
        filename = parts[-1]
        return send_file("/%s/%s" % (dir_name, filename))

    @app.route('/')
    def index():
        data_dict = default_data()

        data_dict['classes'] = [[],  []]
        for key, value in classes_map.items():
            class_ = value[1]
            index = 0 if class_.data_in_root else 1
            data_dict['classes'][index].append(key)
        return render_template("tables.html", **data_dict)

    app.debug = True
    app.run()

