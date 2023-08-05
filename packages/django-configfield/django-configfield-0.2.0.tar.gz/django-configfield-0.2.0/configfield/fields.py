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

from django.forms import ValidationError
from django.utils.translation import ugettext as _

from jsonfield.forms import JSONFormField

from configfield.widgets import ConfigWidget
from configfield.params import Bool, Integer, List, Single, Text


class ConfigFormField(JSONFormField):

    def __init__(self, show_debug=False, *args, **kwargs):
        super(ConfigFormField, self).__init__(*args, **kwargs)
        self.label = kwargs.get('label', _('Configuration'))
        self.widget = ConfigWidget(show_debug)
        self.config = {}

    def set_config_dict(self, config_dict):
        config = {}
        for key, val in config_dict.items():
            if isinstance(val, bool):
                config[key] = Bool(name=key, label=key, default=val)
            elif isinstance(val, list):
                config[key] = List(name=key, label=key, default=val)
            elif isinstance(val, int):
                config[key] = Integer(name=key, label=key, default=val)
            elif len(val) > 250:
                config[key] = Text(name=key, label=key, default=val)
            else:
                config[key] = Single(name=key, label=key, default=val)
            config[key].value = val
        self.set_config(config)

    def set_config(self, config):
        self.config = config
        self.widget.add_config_widgets(config)

    def clean(self, value):
        value = super(ConfigFormField, self).clean(value)
        for name, param in self.config.items():
            if not param.is_valid(value.get(name, None)):
                raise ValidationError(_('Error in "%(name)s" field') % {'name': param.label})
        return value
