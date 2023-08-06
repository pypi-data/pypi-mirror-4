import os


from ojota import Ojota, current_data_code
from flask.helpers import send_file
from flask import Flask, render_template, redirect, request, flash

from helpers import get_ojota_children, get_data_codes, get_form
from renderers import render_field

from jinja2 import FileSystemLoader
template_path = os.path.join(os.path.dirname(__file__), "templates")


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

    @app.route("/new/<name>", methods=['GET', 'POST'])
    @app.route("/edit/<name>/<pk>", methods=['GET', 'POST'])
    def new(name,pk=None):
        data_dict = default_data()
        item = classes_map[name]
        cls = item[1]
        update = False

        if request.method == 'POST' or pk is None:
            data = request.form
        else:
            update = True
            data = cls.get(pk)

        form = get_form(cls, data, update)
        if request.method == 'POST' and form.validate():
            element = cls(**form.data)
            element.save()
            flash('%s successfully saved' % cls.__name__)
            redirect_url = "/%s/%s" % (name, element.primary_key)
            return redirect(redirect_url)
        data_dict['form'] = form
        data_dict['update'] = update
        data_dict['class_name'] = name
        data_dict['class_single_name'] = cls.__name__
        return render_template('form.html', **data_dict)

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
            data_dict['pk'] = pk
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
    app.secret_key = "havaiana-is-awesome"
    app.run()

