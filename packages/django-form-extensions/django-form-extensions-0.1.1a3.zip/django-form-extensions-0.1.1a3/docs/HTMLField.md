HTMLField
=========

The `HTMLField` cleans HTML input based on a whitelist of HTML tags, attributes, and inline-styles. It can also do simple element replacements `<b> -> <strong>`.

Elements
--------

Simply provide a list of allowed tags. 

```python
ALLOWED_TAGS = [
    'a',
    'em',
    'h1',
    'h2',
    'p',
    'strong',
]

class MyForm(forms.Form):
    content = HTMLField(ALLOWED_TAGS)
```

Tags not on the whitelist will appear, HTML-escaped inside their parent.

```HTML
<p>Django has <b>ponies!</b>
```

Will become `Django has &lt;b&gt;ponies!&lt;/b&gt;`.

Attributes
----------

Allowed attributes can be specified in one of two ways. Attributes not in the whitelist will be removed.

```python
ALLOWED_ATTRIBUTES = [
	'class',
    'id',
    'style',
    'title',
]

class MyForm(forms.Form):
    content = HTMLField(ALLOWED_TAGS, ALLOWED_ATTRIBUTES)
```

Attributes can also be whitelisted for a certain tag only or for all tags using the wildcard character `*`

```python
ALLOWED_ATTRIBUTES = [
	'*': ['class', 'id', 'style', 'title'],
    'a': ['href', 'rel'],
    'img': ['alt', 'height', 'src', 'width'],
]

class MyForm(forms.Form):
    content = HTMLField(ALLOWED_TAGS, ALLOWED_ATTRIBUTES)
```

Styles
------

Like allowed attributes, allowed styles can be specified in one of two ways. Styles not in the whitelist will be removed. Also, it is important to add `style` to the attribute whitelist in order for any styles to be allowed.

```python
ALLOWED_STYLES = [
    'border',
    'height',
    'width',
]

class MyForm(forms.Form):
    content = HTMLField(ALLOWED_TAGS, 
                        ALLOWED_ATTRIBUTES,
                        ALLOWED_STYLES)
```

Styles can also be whitelisted for a certian tag only or for all tags using the wildcard character `*`. Also, style properties can use the wildcard charter to allow all variations of that property. E.g. `border*` will whitelist `['border', 'border-left', 'border-right', ...]`.

```python
ALLOWED_STYLES = [
    '*': ['display', 'clear', 'text-align'],
    'img': ['border*', 'margin*', 'padding*', 'height', 'width'],
]

class MyForm(forms.Form):
    content = HTMLField(ALLOWED_TAGS, 
                        ALLOWED_ATTRIBUTES,
                        ALLOWED_STYLES)
```

Element Replacements
--------------------

Element replacements replace one tag with another. It is a dictionary where each key is replaced with it's value.

```python
ELEMENT_REPLACEMENTS = {
    'b': 'strong',
    'i': 'em',
    's': 'del',
    'strike': 'del',
    'u': 'ins',
}

class MyForm(forms.Form):
    content = HTMLField(ALLOWED_TAGS, 
                        ALLOWED_ATTRIBUTES,
                        ALLOWED_STYLES,
                        ELEMENT_REPLACEMENTS)
```



