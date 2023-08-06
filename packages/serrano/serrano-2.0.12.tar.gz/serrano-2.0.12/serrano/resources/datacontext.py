from django.http import HttpResponse
from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from django.views.decorators.cache import never_cache
from restlib2.http import codes
from preserialize.serialize import serialize
from avocado.models import DataContext
from avocado.conf import settings
from serrano.forms import DataContextForm
from .base import ContextViewBaseResource
from . import templates


HISTORY_ENABLED = settings.HISTORY_ENABLED


class DataContextBase(ContextViewBaseResource):
    cache_max_age = 0
    private_cache = True

    template = templates.DataContext

    @classmethod
    def prepare(self, instance):
        obj = serialize(instance, **self.template)

        # If this context is explicitly tied to a model (via the `count`)
        # specify the object names.
        if instance.model:
            opts = instance.model._meta
            obj['object_name'] = opts.verbose_name.format()
            obj['object_name_plural'] = opts.verbose_name_plural.format()

        obj['_links'] = {
            'self': {
                'rel': 'self',
                'href': reverse('serrano:contexts:single', args=[instance.pk]),
            }
        }
        return obj

    @classmethod
    def get_queryset(self, request, **kwargs):
        "Constructs a QuerySet for this user or session."

        if hasattr(request, 'user') and request.user.is_authenticated():
            kwargs['user'] = request.user
        elif request.session.session_key:
            kwargs['session_key'] = request.session.session_key

        # The only case where kwargs is empty is for non-authenticated
        # cookieless agents.. e.g. bots, most non-browser clients since
        # no session exists yet for the agent.
        if not kwargs:
            return DataContext.objects.none()
        return DataContext.objects.filter(**kwargs)


class DataContextsResource(DataContextBase):
    "Resource of active (non-archived) contexts"
    def get(self, request):
        return map(self.prepare, self.get_queryset(request, archived=False))

    def post(self, request):
        form = DataContextForm(request, request.data)

        if form.is_valid():
            instance = form.save(commit=False)
            form.save(archive=HISTORY_ENABLED)
            response = HttpResponse(status=codes.created)
            self.write(request, response, self.prepare(instance))
        else:
            response = HttpResponse(status=codes.unprocessable_entity)
            self.write(request, response, dict(form.errors))
        return response


class DataContextsHistoryResource(DataContextBase):
    "Resource of archived (non-active) contexts"
    def get(self, request):
        return map(self.prepare, self.get_queryset(request, archived=True))


class DataContextResource(DataContextBase):
    "Resource for accessing a single context"
    @classmethod
    def get_object(self, request, pk=None, session=None, **kwargs):
        if not pk and not session:
            raise ValueError('A pk or session must used for the lookup')

        queryset = self.get_queryset(request, **kwargs)

        try:
            if pk:
                return queryset.get(pk=pk)
            else:
                return queryset.get(session=True)
        except DataContext.DoesNotExist:
            pass

    def is_not_found(self, request, response, **kwargs):
        instance = self.get_object(request, **kwargs)
        if instance is None:
            return True
        request.instance = instance

    def get(self, request, **kwargs):
        return self.prepare(request.instance)

    def put(self, request, **kwargs):
        instance = request.instance
        form = DataContextForm(request, request.data, instance=instance)

        if form.is_valid():
            instance = form.save(commit=False)
            if form.count_needs_update:
                # Only recalculated count if conditions exist. This is to
                # prevent re-counting the entire dataset. An alternative
                # solution may be desirable such as pre-computing and
                # caching the count ahead of time.
                if instance.json:
                    instance.count = instance.apply().distinct().count()
                else:
                    instance.count = None
            form.save(archive=HISTORY_ENABLED)
            response = HttpResponse(status=codes.ok)
            self.write(request, response, self.prepare(instance))
        else:
            response = HttpResponse(status=codes.unprocessable_entity)
            self.write(request, response, dict(form.errors))
        return response

    def delete(self, request, **kwargs):
        if request.instance.session:
            return HttpResponse(status=codes.bad_request)
        request.instance.delete()
        return HttpResponse(status=codes.no_content)


single_resource = never_cache(DataContextResource())
active_resource = never_cache(DataContextsResource())
history_resource = never_cache(DataContextsHistoryResource())

# Resource endpoints
urlpatterns = patterns('',
    url(r'^$', active_resource, name='active'),
    url(r'^history/$', history_resource, name='history'),

    # Endpoints for specific contexts
    url(r'^(?P<pk>\d+)/$', single_resource, name='single'),
    url(r'^session/$', single_resource, {'session': True}, name='session'),
)
