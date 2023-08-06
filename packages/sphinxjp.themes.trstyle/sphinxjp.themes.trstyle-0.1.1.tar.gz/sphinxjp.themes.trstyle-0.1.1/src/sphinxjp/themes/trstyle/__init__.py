# -*- coding: utf-8 -*-

from os import path

package_dir = path.abspath(path.dirname(__file__))
template_path = path.join(package_dir, 'templates')


def setup(app):
    app.connect("builder-inited", builder_inited)


def builder_inited(app):
    # unlimit field name size
    app.builder.env.settings['field_name_limit'] = None
