from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class FilteredListMixin(object):
    def filtered_queryset(self, request):
        queryset = self.get_queryset()
        if 'search' in request.GET:
            queryset = queryset.search(request.GET['search'])
        filters = {}
        field_names = queryset.model._meta.get_all_field_names()
        for field, value in request.GET.items():
            field_name = field.split('__')[0]
            if field_name in field_names:
                filters[field] = value
        queryset = queryset.filter(**filters)
        return queryset

    def get(self, request, *args, **kwargs):
        self.queryset = self.filtered_queryset(request)
        return super(FilteredListMixin, self).get(request, *args, **kwargs)


class LoginMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginMixin, self).dispatch(*args, **kwargs)


class OwnershipMixin(object):
    owner_field = 'user'

    def is_owner(self, request, *args, **kwargs):
        self.object = self.get_object()
        return getattr(self.object, self.owner_field, None) == request.user

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        if self.is_owner(request, *args, **kwargs):
            return super(OwnershipMixin, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()


class ObjectOwnerMixin(object):
    owner_model = None
    owner_pk_url_kwarg = 'pk'
    owner_field = 'owner'

    def is_owner(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            queryset =  self.owner_model._default_manager.all()
            owner_pk = kwargs[self.owner_pk_url_kwarg]
            queryset = queryset.filter(pk=owner_pk)
            queryset = queryset.filter(**{self.owner_field: request.user})
            return queryset.exists()
        else:
            return False

    def dispatch(self, request, *args, **kwargs):
        if self.is_owner(request, *args, **kwargs):
            return super(ObjectOwnerMixin, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()



class DeactivateMixin(object):
    deactivation_field = 'active'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        setattr(self.object, self.deactivation_field, False)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())
