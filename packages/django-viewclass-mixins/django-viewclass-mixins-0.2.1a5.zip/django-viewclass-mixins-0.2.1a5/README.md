Django ViewClass Mixins
=======================

Provides some common mixin patterns for Django's View classes.

Installation
------------

Run `pip install django-viewclass-mixins`

View Mixins
-----------

###LoginMixin
Ensures the view is being requested by an authenticated user or redirects to the login page. It behaves the same as the function decorator `login_required`.

###OwnershipMixin
A mixin to single-object views. Ensures the view is by requested by the owner of the requested object.

###DeactivateMixin
A mixin to the DeleteView. Instead of deleting an object it will mark it as inactive instead.

###FilterListMixin
A mixin to the ListView. It will apply filters from the URL querystring to the underlying QuerySet before the list is returned.