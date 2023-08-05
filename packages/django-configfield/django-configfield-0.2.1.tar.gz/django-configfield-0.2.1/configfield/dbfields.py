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


from jsonfield.fields import JSONField
from configfield.fields import ConfigFormField


class ConfigField(JSONField):

    def formfield(self, **kwargs):
        return super(JSONField, self).formfield(form_class=ConfigFormField, **kwargs)


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ['^configfield\.dbfields\.ConfigField'])
except ImportError:
    pass
