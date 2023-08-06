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

###StaffRequiredMixin
Ensures the view is being request by an authenticated user that is marked as staff.

###SuperuserRequiredMixin
Ensures the view is being request by an authenticated user that is marked as a superuser.

###OwnershipMixin
A mixin to single-object views. Ensures the view is by requested by the owner of the requested object.

###DeactivateMixin
A mixin to the DeleteView. Instead of deleting an object it will mark it as inactive instead.

###FilterListMixin
A mixin to the ListView. It will apply filters from the URL querystring to the underlying QuerySet before the list is returned.

###ModelFormSetMixin
A mixin to the CreateView and UpdateView. It take a list of FormSets and validates and saves them along with the main model.

###HttpCacheMixin
A mixin to any View. It has methods for setting HTTP cache headers like *Cache-Control*, *Vary*, *ETag*, and *Last-Modified*.