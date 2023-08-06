from django.forms.fields import Field, CharField, FileField, ImageField
from django.forms.widgets import Textarea
from form_extensions.widgets import HoneypotWidget, MultiFileInput
from django.core.exceptions import ValidationError
from django.core import validators
from form_extensions.utils import bleach, replace_elements, remove_empty_paragraphs
import re


EMPTY_VALUES = (None, '')
CURRENCY_RE = re.compile(r'^\$?\d+(,\d{3})*(\.\d{0,2})?$')
CREDIT_CARD_PATTERNS = {
    'Visa': '^4([0-9]{12,15})$',
    'MasterCard': '^5[12345]([0-9]{14})$',
    'American Express': '^3[47][0-9]{13}$',
    'Discover': '^6(?:011|5[0-9]{2})[0-9]{12}$',
    'Diners Club': '^3(?:0[0-5]|[68][0-9])[0-9]{11}$',
    'JCB': '^(?:2131|1800|35\d{3})\d{11}$',
}


class HoneypotField(Field):
    widget = HoneypotWidget

    def clean(self, value):
        if self.initial in EMPTY_VALUES and value in EMPTY_VALUES or value == self.initial:
            return value
        raise ValidationError('Anti-spam field changed in value.')


class HTMLField(Field):
    widget = Textarea

    def __init__(self, allowed_tags, allowed_attributes={}, allowed_styles={}, element_replacements={}, *args, **kwargs):
        super(HTMLField, self).__init__(*args, **kwargs)
        self.allowed_tags = allowed_tags
        self.allowed_attributes = allowed_attributes
        self.allowed_styles = allowed_styles
        self.element_replacements = element_replacements

    def clean(self, value):
        value = replace_elements(value, self.element_replacements)
        value = remove_empty_paragraphs(value)
        value = bleach(value, self.allowed_tags, self.allowed_attributes, self.allowed_styles)
        return super(HTMLField, self).clean(value)


class USCurrencyField(CharField):
    def clean(self, value):
        if value in validators.EMPTY_VALUES:
            return
        if not re.match(CURRENCY_RE, value):
            raise ValidationError('Enter a valid amount in U.S. dollars.')
        value = value.replace('$', '').replace(',', '')
        return super(USCurrencyField, self).clean(value)


class CreditCardField(CharField):
    def init(self, max_length=19, *args, **kwargs):
        super(CreditCardField, self).__init__(max_length, *args, **kwargs)

    def clean(self, value):
        if value in validators.EMPTY_VALUES:
            return
        value = value.replace(' ', '').replace('-', '')
        num = [int(digit) for digit in str(value)]
        valid = not sum(num[::-2] + [sum(divmod(d * 2, 10)) for d in num[-2::-2]]) % 10
        if not valid:
            raise ValidationError('Enter a valid credit card number.')
        return super(CreditCardField, self).clean(value)



class MultiFileField(FileField):
    widget = MultiFileInput
    default_error_messages = {
        'min_num': u"Ensure at least %(min_num)s files are uploaded (received %(num_files)s).",
        'max_num': u"Ensure at most %(max_num)s files are uploaded (received %(num_files)s).",
    }

    def __init__(self, *args, **kwargs):
        self.min_num = kwargs.pop('min_num', 0)
        self.max_num = kwargs.pop('max_num', None)
        super(MultiFileField, self).__init__(*args, **kwargs)

    def to_python(self, data):
        ret = []
        for item in data:
            ret.append(super(MultiFileField, self).to_python(item))
        return ret

    def validate(self, data):
        super(MultiFileField, self).validate(data)
        num_files = len(data)
        if num_files < self.min_num:
            raise ValidationError(self.error_messages['min_num'] % {'min_num': self.min_num, 'num_files': num_files})
        elif self.max_num and  num_files > self.max_num:
            raise ValidationError(self.error_messages['max_num'] % {'max_num': self.max_num, 'num_files': num_files})


class MultiImageField(ImageField):
    widget = MultiFileInput
    default_error_messages = {
        'min_num': u"Ensure at least %(min_num)s files are uploaded (received %(num_files)s).",
        'max_num': u"Ensure at most %(max_num)s files are uploaded (received %(num_files)s).",
    }

    def __init__(self, *args, **kwargs):
        self.min_num = kwargs.pop('min_num', 0)
        self.max_num = kwargs.pop('max_num', None)
        super(MultiImageField, self).__init__(*args, **kwargs)

    def to_python(self, data):
        ret = []
        for item in data:
            ret.append(super(MultiImageField, self).to_python(item))
        return ret

    def validate(self, data):
        super(MultiImageField, self).validate(data)
        num_files = len(data)
        if num_files < self.min_num:
            raise ValidationError(self.error_messages['min_num'] % {'min_num': self.min_num, 'num_files': num_files})
        elif self.max_num and  num_files > self.max_num:
            raise ValidationError(self.error_messages['max_num'] % {'max_num': self.max_num, 'num_files': num_files})
