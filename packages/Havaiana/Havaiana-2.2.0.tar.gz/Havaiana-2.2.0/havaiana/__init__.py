import os


from ojota import Ojota, current_data_code
from flask.helpers import send_file
from flask import Flask, render_template, redirect, request, flash

from helpers import get_ojota_children, get_data_codes, get_form
from renderers import render_field

from jinja2 import FileSystemLoader


class Site(object):
    def __init__(self, package, title="Havaiana",
                 renderers=None):
        if renderers is None:
            renderers  = []

        self.renderers = renderers
        self.package = package
        self.title = title
        self.template_path = os.path.join(os.path.dirname(__file__),
                                          "templates")
        self.editable = True
        self.deletable = True
        self.sortable = True

        self._create_app()

    def _default_data(self):
        data = {}

        data['title'] = self.title
        data['data_code'] = Ojota.CURRENT_DATA_CODE
        if data['data_code'] == "":
            data['data_code'] = "Root"
        data['data_codes'] = get_data_codes()
        data['editable'] = self.editable
        data['deletable'] = self.deletable
        data['sortable'] = self.sortable
        return data

    def _create_app(self):
        self.classes = get_ojota_children(self.package)
        self.app = Flask(__name__)
        self.app.jinja_loader = FileSystemLoader(self.template_path)

    def _create_map(self):
        self.classes_map = {}

        for item in self.classes:
           self.classes_map[item[1].plural_name] = item

    def serve(self):
        self._create_map()

        self.app.add_url_rule('/change-data-code/<data_code>', 'change_data_code',
                          self.change_data_code)
        self.app.add_url_rule("/new/<name>", "new", self.new,
                          methods=['GET', 'POST'])
        self.app.add_url_rule("/edit/<name>/<pk_>", "new", self.new,
                              methods=['GET', 'POST'])
        self.app.add_url_rule("/delete/<name>/<pk_>", "delete", self.delete,
                              methods=['GET', 'POST'])
        self.app.add_url_rule("/<name>", "table", self.table)
        self.app.add_url_rule("/<name>/<pk_>", "table", self.table)
        self.app.add_url_rule('/media/<path:filename>', "custom_static",
                              self.custom_static)
        self.app.add_url_rule('/absolute//<path:filename>',
                              "custom_absolute_static",
                              self.custom_absolute_static)
        self.app.add_url_rule('/', "index", self.index)

        @self.app.errorhandler(404)
        def page_not_found(self, e):
            data_dict = self._default_data()
            data_dict['message'] = "Ugly <strong>404</strong> is Ugly"
            return render_template('404.html', **data_dict), 404

        self.app.debug = True
        self.app.secret_key = "havaiana-is-awesome"
        self.app.run(host="0.0.0.0")

    def change_data_code(data_code):
        if data_code == 'Root':
            data_code = ''
        current_data_code(data_code)
        return redirect('/')

    def new(self, name, pk_=None):
        data_dict = self._default_data()
        if pk_ and not self.editable:
            data_dict['message'] = "Edition is not supported"
            return render_template("404.html", **data_dict), 403
        else:
            item = self.classes_map[name]
            cls = item[1]
            update = False

            if request.method == 'POST' or pk_ is None:
                data = request.form
            else:
                update = True
                data = cls.get(pk_)

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

    def delete(self, name, pk_=None):
        if self.deletable:
            item = self.classes_map[name]
            cls = item[1]
            element = cls.get(pk_)
            if request.method == 'GET':
                data_dict = self._default_data()
                data_dict['element'] = element
                data_dict['class_name'] = name
                data_dict['pk'] = pk_
                return render_template("confirm_delete.html", **data_dict)
            else:
                flash('%s successfully deleted' % element)
                element.delete()
                redirect_url = "/%s" % name
                return redirect(redirect_url)
        else:
            data_dict = self._default_data()
            data_dict['message'] = "Deletion is not supported"
            return render_template("404.html", **data_dict), 403

    def table(self, name, pk_=None):
        data_dict = self._default_data()
        try:
            item = self.classes_map[name]
        except KeyError:
            data_dict['message'] = "The class <strong>%s</strong> does not exist"  % name
            return render_template("404.html", **data_dict), 404

        cls = item[1]
        class_renderers = [renderer[1:] for renderer in self.renderers
                            if renderer[0] == item[0]]
        data_dict['class_name'] = name
        if pk_ is None:
            if self.sortable:
                order = request.values.get('order')
            else:
                order = None

            data_dict['items'] = cls.all(sorted=order)

            if self.sortable:
                fields = []
                for element in data_dict['items']:
                    fields.extend(element.fields)
                fields = set(fields)
                data_dict['order_fields'] = fields

            template = 'table.html'
        else:
            params = {getattr(cls, "pk_field"): pk_}
            item = cls.get(**params)
            if item is None:
                data_dict['message'] = "The item with id <strong>%s</strong> does not exist for class %s"  % (pk_, name)
                return render_template("404.html", **data_dict), 404
            attrs = []
            for field in item.fields:
                attrs.append(render_field(field, item, class_renderers))
            for bw_rel in item.backwards_relations:
                attrs.append(render_field(bw_rel, item, class_renderers,
                                            True))

            data_dict['item'] = item
            data_dict['pk'] = pk_
            data_dict['attrs'] = attrs
            template = 'item.html'
        return render_template(template, **data_dict)

    def custom_static(self, filename):
        parts = filename.split("/")
        dir_name = "/".join(parts[:-1])
        filename = parts[-1]
        return send_file("templates/static/%s/%s" % (dir_name, filename))

    def custom_absolute_static(self, filename):
        parts = filename.split("/")
        dir_name = "/".join(parts[:-1])
        filename = parts[-1]
        return send_file("/%s/%s" % (dir_name, filename))

    def index(self):
        data_dict = self._default_data()

        data_dict['classes'] = [[],  []]
        for key, value in self.classes_map.items():
            class_ = value[1]
            index = 0 if class_.data_in_root else 1
            data_dict['classes'][index].append(key)
        return render_template("tables.html", **data_dict)




