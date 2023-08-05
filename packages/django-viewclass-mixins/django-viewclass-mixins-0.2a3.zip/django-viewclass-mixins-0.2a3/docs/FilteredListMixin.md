FilteredListMixin
=================

A mixin to the ListView. It will apply filters from the URL querystring to the underlying QuerySet before the list is returned.

Only valid field names will be applied to the QuerySet all other keys in the querystring will be ignored.

```python
from django.views.generic import DeleteView
from viewclass_mixins.views import DeactivateMixin

class ObjectList(DeactivateMixin, DeleteView):
    model = Object
    ...
```


Example URLs:

Equality:

`/objects/?active=1`

Comparison Operators:

`/objects/?created__gte=2012-01-01`

Relations:

`/objects/?properties__name=round`

Combinations:

`/objects/?active=1&color=blue`