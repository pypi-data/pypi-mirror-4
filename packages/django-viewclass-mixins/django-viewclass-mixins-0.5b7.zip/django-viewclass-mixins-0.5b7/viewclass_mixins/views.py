from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.utils.cache import patch_response_headers, patch_vary_headers


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


class StaffRequiredMixin(LoginMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super(StaffRequiredMixin, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()


class SuperuserRequiredMixin(LoginMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super(SuperuserRequiredMixin, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()


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
            queryset = self.owner_model._default_manager.all()
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


class ModelFormSetMixin(object):
    formset_classes = []

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formsets = self.get_formsets()
        return self.render_to_response(self.get_context_data(form=form,
                                                             formsets=formsets))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formsets = self.get_formsets()
        forms = [form] + formsets
        if all([frm.is_valid() for frm in forms]):
            return self.form_valid(form, formsets)
        return self.form_invalid(form, formsets)

    def form_valid(self, form, formsets):
        self.object = form.save()
        for formset in formsets:
            formset.save()
        return super(ModelFormSetMixin, self).form_valid(form)

    def form_invalid(self, form, formsets):
        return self.render_to_response(self.get_context_data(form=form,
                                                             formsets=formsets))

    def get_formsets(self):
        formset_kwargs = self.get_formset_kwargs()
        return [formset_class(**formset_kwargs) for formset_class in self.formset_classes]

    def get_formset_kwargs(self):
        """
        Returns the keyword arguments for instanciating the form.
        """
        kwargs = {
            'initial': self.get_initial(),
            'instance': self.object,
        }
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_object(self, queryset=None):
        try:
            return super(ModelFormSetMixin, self).get_object(queryset)
        except AttributeError:
            if self.model:
                model = self.model
            else:
                if queryset is None:
                    queryset = self.get_queryset()
                model = queryset.model
            return model()


class HttpCacheMixin(object):
    cache_timeout = 60
    cache_varies = ['Accept']

    def get_cache_timeout(self):
        return self.cache_timeout

    def get_cache_varies(self):
        return self.cache_varies

    def get_last_modified(self):
        return None

    def get_etag(self, ):
        return None

    @classmethod
    def cacheable(self, request, response):
        return (request.method in ['GET', 'HEAD', 'PUT'] and
                response.status_code in [200, 203, 206, 410])

    def dispatch(self, request, *args, **kwargs):
        response = super(HttpCacheMixin, self).dispatch(request, *args, **kwargs)
        if self.cacheable(request, response):
            last_modified = self.get_last_modified()
            if last_modified is not None:
                response['Last-Modified'] = last_modified
            etag = self.get_etag()
            if etag is not None:
                response['ETag'] = etag
            cache_timeout = int(self.get_cache_timeout())
            patch_response_headers(response, cache_timeout)
            cache_varies = self.get_cache_varies()
            if len(cache_varies):
                patch_vary_headers(response, cache_varies)
        return response
