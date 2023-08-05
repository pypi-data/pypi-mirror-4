from django import forms
from itertools import chain
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.forms.util import flatatt
from django.conf import settings


EMPTY_VALUES = (None, '')


class HoneypotWidget(forms.TextInput):
    is_hidden = True
    def __init__(self, attrs=None, html_comment=False, *args, **kwargs):
        self.html_comment = html_comment
        super(HoneypotWidget, self).__init__(attrs, *args, **kwargs)
        if not self.attrs.has_key('class'):
            self.attrs['style'] = 'display:none'
    def render(self, *args, **kwargs):
        value = super(HoneypotWidget, self).render(*args, **kwargs)
        if self.html_comment:
            value = '<!-- %s -->' % value
        return value


class DataList(forms.TextInput):
    def __init__(self, attrs=None, choices=()):
        super(DataList, self).__init__(attrs)
        self.choices = list(choices)

    def render(self, name, value, attrs={}, choices=()):
        attrs['list'] = u'id_%s_list' % name
        output = super(DataList, self).render(name, value, attrs)
        output += u'\n' + self.render_options(name, choices)
        return output

    def render_options(self, name, choices):
        output = []
        output.append(u'<datalist id="id_%s_list" style="display:none">' % name)
        output.append(u'<select name="%s_select"' % name)
        for option in chain(self.choices, choices):
            output.append(u'<option value="%s" />' % conditional_escape(force_unicode(option)))
        output.append(u'</select>')
        output.append(u'</datalist>')
        return u'\n'.join(output)


class MultiFileInput(forms.FileInput):
    def render(self, name, value, attrs={}):
        attrs['multiple'] = 'multiple'
        return super(MultiFileInput, self).render(name, None, attrs=attrs)

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        else:
            return [files.get(name)]


class FileMultiInput(forms.FileInput):
    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        else:
            return [files.get(name)]


class ImageInput(forms.FileInput):
    def __init__(self, size, attrs=None):
        self.size = size
        super(ImageInput, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        if value:
            if hasattr(value, 'get_thumbnail') and value.storage.exists(value):
                thumbnail = value.get_thumbnail({'size': self.size})
                image_attrs = {
                    'class': u'image-preview',
                    'src': thumbnail.url,
                    'height': thumbnail.height,
                    'width': thumbnail.width,
                    'style': 'max-width: %spx; max-height: %spx;' % self.size,
                }
            else:
                image_attrs = {
                    'class': u'image-preview',
                    'src': settings.MEDIA_URL + str(value),
                    'style': 'max-width: %spx; max-height: %spx;' % self.size,
                }
            image = u'<img%s />' % flatatt(image_attrs)
        else:
            image_attrs = {
                'class': u'image-preview',
                'src': settings.STATIC_URL + 'images/blank-image.jpg',
                'style': 'max-width: %spx; max-height: %spx;' % self.size,
            }
            image = u'<img%s />' % flatatt(image_attrs)
        return mark_safe(image) + super(ImageInput, self).render(name, value, attrs)
