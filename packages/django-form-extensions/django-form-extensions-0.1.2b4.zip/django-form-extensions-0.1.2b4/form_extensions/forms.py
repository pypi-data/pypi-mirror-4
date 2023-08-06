from django.forms import BaseForm


class DeclarativeFieldsMetaclass(type):
    """
    Metaclass that converts Field attributes to a dictionary called
    'base_fields', taking into account parent class 'base_fields' as well.
    """
    def __new__(cls, name, bases, attrs):
        for form_class in attrs['form_classes']:
            attrs['base_fields'] += get_declared_fields(bases, form_class.attrs)
        new_class = super(DeclarativeFieldsMetaclass, cls).__new__(cls, name, bases, attrs)
        if 'media' not in attrs:
            new_class.media = media_property(new_class)
        return new_class


class MultiForm(BaseForm):
    __metaclass__ = DeclarativeFieldsMetaclass
