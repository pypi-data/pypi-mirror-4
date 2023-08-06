Django Form Extensions
======================

Django form extensions implements serveral usefull Field and Widget classes for Django forms.

Installation
------------

Run `pip install django-form-extensions`

Fields
------

###HoneypotField
Presents an alluring target for robo-spammers. Raises a form error if tampered with.

###HTMLField
Whitelist HTML tags, attributes, and styles and return the resulting HTML with illegal items stripped out.

###USCurrencyField
Take in all common forms of representing US currency and return a decimal value.

###CreditCardField
Only accepts mathmatically correct credit card numbers.

###MultiFileField
Allows a single field to take multiple file uploads.

Widgets
-------

###DataList
Generates the HTML5 datalist element which is used for autocomplete.

###MultiFileInput
Renders `<input type="file" multiple="multiple" />` and it's Python value is a list of files.

###FileMultiInput
Takes several instances of `<input type="file" />` combines them for it's Python value which is a list of files.

###ImageInput
Renders a thumbnail of the image before the `FileInput` widget.
