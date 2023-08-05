# Copyright (c) 2010 by Yaco Sistemas
#
# This file is part of django-configfield.
#
# django-configfield is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django-configfield is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with django-configfield.  If not, see <http://www.gnu.org/licenses/>.

from django.forms import widgets
from django.forms.util import flatatt
from django.utils import simplejson as json
from django.utils.html import linebreaks
from django.utils.safestring import mark_safe


class ParamWidget(widgets.Widget):

    def __init__(self, param, attrs=None):
        super(ParamWidget, self).__init__(attrs)
        self.param = param

    def value_from_datadict(self, data, files, name):
        """ Returns a dictionary with only the value for widget param.
            ConfigWidget will compress all into a complete dictionary """
        value = self.param.get_value_from_datadict(data, name)
        return {self.param.name: value}

    def render(self, name, value, attrs=None):
        """ rendering function. note: value will be a config param instance """
        widget_attrs = self.build_attrs(attrs, name=name)
        flat_attrs = flatatt(widget_attrs)
        return self.param.render(name, mark_safe(flat_attrs))


class ConfigWidget(widgets.MultiWidget):

    def __init__(self, show_debug=False, attrs=None):
        self.config = None  # to be filled in registry model admin
        self.show_debug = show_debug
        super(ConfigWidget, self).__init__(widgets=[], attrs=attrs)

    def add_config_widgets(self, config):
        self.config = config
        for param in self.config.values():
            self.widgets.append(ParamWidget(param))

    def decompress(self, value):
        if value and getattr(self.config, 'values', []):
            param_list = []
            for param in self.config.values():
                param.value = value.get(param.name, param.value)
                param_list.append(param)
            return param_list
        # if all None we returns n-Nones
        return [None] * len(self.widgets)

    def value_from_datadict(self, data, files, name):
        value_list = super(ConfigWidget, self).value_from_datadict(data,
                                                                   files, name)
        value = dict()
        for v in value_list:
            value.update(v)
        return value

    def render(self, name, value, attrs=None):
        """ rendering function. note: value will be a config param instance """
        widgets_render = super(ConfigWidget, self).render(name, value, attrs)
        json_value = linebreaks(json.dumps(value, indent=2))
        rendered = widgets_render
        if self.show_debug:
            rendered += u"""<div class="configDebug">
            <label>JSON Debug:</label>
            <pre>%s</pre>
            </div>""" % json_value
        return mark_safe('<div class="configField">%s</div>' % rendered)
