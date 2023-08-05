Django Model Validators
=======================

Django model validators adds a few common validators in addition to Django's [built-in validators](https://docs.djangoproject.com/en/dev/ref/validators/).

Installation
------------

Run `pip install django-model-validators`

Validators
----------

###FileTypeValidator
Ensures an upload file name ends in an extension.

```python
from django.db import models
from model_validators.validators import FileTypeValidator

class MyModel(models.Model):
    even_field = models.IntegerField(validators=[FileTypeValidator('zip')])
```

It can also be passed a list of extensions:

```python
from django.db import models

class MyModel(models.Model):
    even_field = models.IntegerField(validators=[FileTypeValidator(['zip', 'txt', 'pdf'])])
```

###NumericRangeValidator
Ensure the field value falls within the specified range.

```python
from django.db import models
from model_validators.validators import NumericRangeValidator

class MyModel(models.Model):
    rating = models.PositiveIntegerField(validators=[NumericRangeValidator(1, 10)])
```
