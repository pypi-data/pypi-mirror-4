ObjectOwnerMixin
================

A mixin to single-object views. Ensures the view is by requested by the owner of the requested object.

The `owner_model` is required when declaring your class. This is the model you are checking ownership of.

The `owner_pk_url_kwarg` is the keyword argument of the URL that corresponds the the owner model's primary key. The default value is `pk`.

The `owner_field` is  the field name on the owner model that is the foreign key to the `User` model. Ownership of the owner model will be determined by comparing this field value to `request.user`. The default value is `owner`.

```python
from django.views.generic import UpdateView
from viewclass_mixins.views import ObjectOwnerMixin

class ObjectUpdate(ObjectOwnerMixin, UpdateView):
    owner_model = Object
    owner_pk_url_kwarg = 'slug'
    owner_field = 'user'
    ...
```