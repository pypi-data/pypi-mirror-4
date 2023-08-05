#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""ReST API for Ralph's business models
   ------------------------------------

Done with TastyPie."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf import settings
from tastypie import fields
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.cache import SimpleCache
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.resources import ModelResource as MResource
from tastypie.throttle import CacheThrottle

from ralph.business.models import Venture, VentureRole, Department

THROTTLE_AT = settings.API_THROTTLING['throttle_at']
TIMEFREME = settings.API_THROTTLING['timeframe']
EXPIRATION = settings.API_THROTTLING['expiration']

class VentureResource(MResource):
    devices = fields.ToManyField('ralph.discovery.api.DevResource', 'device')
    roles = fields.ToManyField('ralph.business.api.RoleResource', 'venturerole')
    department = fields.ForeignKey('ralph.business.api.DepartmentResource',
        'department', null=True, full=True)

    class Meta:
        queryset = Venture.objects.all()
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            'id': ALL,
            'name': ALL,
            'symbol': ALL,
            'data_center': ALL_WITH_RELATIONS,
            'show_in_ralph': ALL,
        }
        excludes = ('save_priorities', 'max_save_priority',)
        cache = SimpleCache()
        limit = 10
        throttle = CacheThrottle(throttle_at=THROTTLE_AT, timeframe=TIMEFREME,
                                expiration=EXPIRATION)


class VentureLightResource(MResource):
    department = fields.ForeignKey('ralph.business.api.DepartmentResource',
        'department', null=True, full=True)

    class Meta:
        queryset = Venture.objects.all()
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            'id': ALL,
            'name': ALL,
            'symbol': ALL,
            'data_center': ALL_WITH_RELATIONS,
            'show_in_ralph': ALL,
        }
        excludes = ('save_priorities', 'max_save_priority',)
        cache = SimpleCache()
        throttle = CacheThrottle(throttle_at=THROTTLE_AT, timeframe=TIMEFREME,
                                expiration=EXPIRATION)

    def dehydrate_resource_uri(self, bundle):
        uri = super(VentureLightResource, self).dehydrate_resource_uri(bundle)
        return uri.replace('venturelight', 'venture')


class RoleResource(MResource):
    venture = fields.ForeignKey(VentureResource, 'venture', null=True)
    parent = fields.ForeignKey('ralph.business.api.RoleResource',
        'parent', null=True)

    class Meta:
        queryset = VentureRole.objects.all()
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            'id': ALL,
            'name': ALL,
            'venture': ALL_WITH_RELATIONS,
        }
        excludes = ('save_priorities', 'max_save_priority',)
        cache = SimpleCache()
        throttle = CacheThrottle(throttle_at=THROTTLE_AT, timeframe=TIMEFREME,
                                expiration=EXPIRATION)


class DepartmentResource(MResource):
    class Meta:
        queryset = Department.objects.all()
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            'id': ALL,
            'name': ALL,
        }
        cache = SimpleCache()
        excludes = ('icon',)
        throttle = CacheThrottle(throttle_at=THROTTLE_AT, timeframe=TIMEFREME,
                                expiration=EXPIRATION)
