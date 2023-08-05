Deactivate Mixin
================
A mixin to the DeleteView. Instead of deleting an object it will mark it as inactive instead.

The default `deactivation_field` name is `'active'`. This can be overridden in your view definition.

```python
from django.views.generic import DeleteView
from viewclass_mixins.views import DeactivateMixin

class ObjectDeactivate(DeactivateMixin, DeleteView):
    deactivation_field = 'live'
    ...
```
 