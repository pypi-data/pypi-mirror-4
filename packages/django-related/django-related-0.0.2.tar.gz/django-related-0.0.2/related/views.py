from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect, Http404
from django.contrib import messages
from django.db import IntegrityError


class GetExistingMixin(object):
    existing_form_class = None
    existing_form_field = None
    existing_form_initial = None
    existing_pk_field = 'pk'
    existing_slug_field = 'slug'
    existing_request_pk_key = 'pk'
    existing_request_slug_key = 'slug'
    existing_redirect_url = None

    def get_existing_redirect_url(self, existing_object):
        if not self.existing_redirect_url:
            raise ImproperlyConfigured('existing_redirect_url not defined')
        return self.existing_redirect_url

    def get_existing_kwargs(self):
        lookup_kwargs = dict()
        pk_param = self.request.REQUEST.get(self.existing_request_pk_key)

        if pk_param:
            lookup_kwargs[self.existing_pk_field] = pk_param
            return lookup_kwargs

        slug_param = self.request.REQUEST.get(self.existing_request_slug_key)
        if slug_param:
            lookup_kwargs[self.existing_slug_field] = slug_param
            return lookup_kwargs

        lookup_kwargs = None
        return lookup_kwargs

    def get_existing_from_request(self):
        lookup_kwargs = self.get_existing_kwargs()

        if not lookup_kwargs:
            return

        try:
            return self.model.objects.get(**lookup_kwargs)
        except [self.model.DoesNotExist, self.model.MultipleObjectsReturned]:
            pass

    def get_existing_form_class(self):
        return self.existing_form_class

    def get_existing_form_initial(self):
        if not self.existing_form_initial:
            return dict()
        else:
            return initial()

    def get_existing_form_kwargs(self):
        kwargs = dict(initial=self.get_existing_form_initial())
        if self.request.method in ('POST', 'PUT'):
            kwargs.update(dict(data=self.request.POST))
        return kwargs

    def get_existing_form(self, *args, **kwargs):
        form_class = self.get_existing_form_class()
        form_kwargs = self.get_existing_form_kwargs()
        form_kwargs.update(kwargs)
        return form_class(*args, **form_kwargs)

    def get_existing_from_form(self):
        form = self.get_existing_form()
        if form.is_valid():
            return form.cleaned_data[self.existing_form_field]

    def get_existing(self):
        if self.existing_form_class:
            return self.get_existing_from_form()
        else:
            return self.get_existing_from_request()

    def get_context_data(self, *arg, **kwarg):
        context = dict()

        if self.get_existing_form_class():
            if self.request.method == 'GET' and self.request.GET:
                form = self.get_existing_form(data=self.request.GET)
            else:
                form = self.get_existing_form()

            context['existing_form'] = form

        context.update(
            super(GetExistingMixin, self).get_context_data(*arg, **kwarg)
        )
        return context

    def post(self, request, *args, **kwargs):
        existing_object = self.get_existing()

        if (existing_object):
            return HttpResponseRedirect(
                self.get_existing_redirect_url(existing_object))

        return super(GetExistingMixin, self).post(request, *args, **kwargs)


class CreateWithRelatedMixin(object):
    related_model = None
    related_field = None
    related_404_redirect_url = None
    related_404_message = '%s does not exist'
    related_pk_field = 'pk'
    related_pk_url_kwarg = 'pk'
    related_slug_field = 'slug'
    related_slug_url_kwarg = 'slug'
    integrity_error_message = 'Such record already exists'

    def get_related_404_url(self):
        return self.related_404_redirect_url

    def get_related_404_message(self):
        return self.related_404_message % self.related_model._meta.verbose_name

    def related_not_found(self):
        messages.error(self.request, self.get_related_404_message())
        return  HttpResponseRedirect(self.get_related_404_url())

    def get_related_field(self):
        return self.related_field or self.related_model._meta.verbose_name

    def get_object_kwargs(self):
        object_kwargs = dict()
        pk = self.kwargs.get(self.related_pk_url_kwarg)
        if pk:
            object_kwargs[self.related_pk_field] = pk
            return object_kwargs

        slug = self.kwargs.get(self.related_slug_url_kwarg)
        if slug:
            object_kwargs[self.related_slug_url_kwarg] = slug
            return object_kwargs

        object_kwargs = None
        return object_kwargs

    def get_related_object(self):
        if not self.related_model:
            raise ImproperlyConfigured('related_model attribute not defined')

        object_kwargs = self.get_object_kwargs()

        if not object_kwargs:
            return None

        return self.related_model.objects.get(**object_kwargs)

    def get_integrity_error_message(self):
        return self.integrity_error_message

    def related_object_not_found(self):
        related_404_url = self.get_related_404_url()
        if related_404_url:
            return HttpResponseRedirect(related_404_url)
        else:
            raise Http404()

    def form_valid(self, form):
        try:
            related_object = self.get_related_object()
        except self.related_model.DoesNotExist:
            return self.related_object_not_found(self);

        self.object = self.model(**form.cleaned_data)
        setattr(self.object, self.get_related_field(), related_object)

        try:
            self.object.save()
        except IntegrityError:
            messages.error(self.request, self.get_integrity_error_message())
            return super(CreateWithRelatedMixin, self).form_invalid(form)

        return HttpResponseRedirect(self.get_success_url())
