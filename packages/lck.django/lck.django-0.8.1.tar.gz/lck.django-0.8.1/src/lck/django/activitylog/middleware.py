#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 by Łukasz Langa
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.db import models as db

try:
    from django.utils.timezone import now
except ImportError:
    now = datetime.now

from lck.django.activitylog.models import UserAgent, IP, ProfileIP,\
    ProfileUserAgent, Backlink, ACTIVITYLOG_PROFILE_MODEL
from lck.django.common import model_is_user, remote_addr

_backlink_url_max_length = Backlink._meta.get_field_by_name(
    'url')[0].max_length
_backlink_referrer_max_length = Backlink._meta.get_field_by_name(
    'referrer')[0].max_length
BACKLINKS_LOCAL_SITES = getattr(settings, 'BACKLINKS_LOCAL_SITES',
    'current')


class ActivityMiddleware(object):
    """Updates the `last_active` profile field for every logged in user with
    the current timestamp. It pragmatically stores a new value every 40 seconds
    (one third of the seconds specified ``CURRENTLY_ONLINE_INTERVAL`` setting).
    """

    def update_backlinks(self, request, current_site):
        backlink, backlink_created = Backlink.concurrent_get_or_create(
            site=current_site,
            url=request.META['PATH_INFO'][:_backlink_url_max_length],
            referrer=request.META['HTTP_REFERER'][:_backlink_referrer_max_length])
        if not backlink_created:
            # we're not using save() to bypass signals etc.
            Backlink.objects.filter(id=backlink.id).update(modified=now(),
                visits=db.F('visits') + 1)

    def process_request(self, request):
        # FIXME: don't use concurrent_get_or_create for bl, pip and pua to
        # maximize performance
        _now = now()
        seconds = getattr(settings, 'CURRENTLY_ONLINE_INTERVAL', 120)
        delta = _now - timedelta(seconds=seconds)
        users_online = cache.get('users_online', {})
        guests_online = cache.get('guests_online', {})
        users_touched = False
        guests_touched = False
        if request.user.is_authenticated():
            users_online[request.user.id] = _now
            users_touched = True
            if model_is_user(ACTIVITYLOG_PROFILE_MODEL):
                profile = request.user
            else:
                profile = request.user.get_profile()
        else:
            guest_sid = request.COOKIES.get(settings.SESSION_COOKIE_NAME, '')
            guests_online[guest_sid] = _now
            guests_touched = True
            profile = None
        for user_id in users_online.keys():
            if users_online[user_id] < delta:
                users_touched = True
                del users_online[user_id]
        if users_touched:
            cache.set('users_online', users_online, 60*60*24)
        for guest_id in guests_online.keys():
            if guests_online[guest_id] < delta:
                guests_touched = True
                del guests_online[guest_id]
        if guests_touched:
            cache.set('guests_online', guests_online, 60*60*24)
        ip, _ = IP.concurrent_get_or_create(address=remote_addr(request))
        if 'HTTP_USER_AGENT' in request.META:
            agent, _ = UserAgent.concurrent_get_or_create(name=request.META[
                'HTTP_USER_AGENT'])
        else:
            agent = None
        if profile:
            last_active = profile.last_active
            if not last_active or 3 * (_now - last_active).seconds > seconds:
                # we're not using save() to bypass signals etc.
                profile.__class__.objects.filter(pk = profile.pk).update(
                    last_active = _now)
            pip, _ = ProfileIP.concurrent_get_or_create(ip=ip, profile=profile)
            ProfileIP.objects.filter(pk = pip.pk).update(
                modified = _now)
            if agent:
                pua, _ = ProfileUserAgent.concurrent_get_or_create(agent=agent,
                    profile=profile)
                ProfileUserAgent.objects.filter(pk = pua.pk).update(
                    modified = _now)
        request.ip = ip
        request.agent = agent

    if BACKLINKS_LOCAL_SITES == 'current':
        def process_response(self, request, response):
            current_site = Site.objects.get(id=settings.SITE_ID)
            try:
                ref = request.META.get('HTTP_REFERER', '').split('//')[1]
                if response.status_code // 100 == 2 and not \
                    (ref == current_site.domain or ref.startswith(
                    current_site.domain + '/')):
                    self.update_backlinks(request, current_site)
            except (IndexError, UnicodeDecodeError):
                pass
            return response
    elif BACKLINKS_LOCAL_SITES == 'all':
        def process_response(self, request, response):
            try:
                ref = request.META.get('HTTP_REFERER', '').split('//')[1]
                if response.status_code // 100 == 2:
                    for site in Site.objects.all():
                        if ref == site.domain or \
                            ref.startswith(site.domain + '/'):
                            break
                        if site.id == settings.SITE_ID:
                            current_site = site
                    else:
                        self.update_backlinks(request, current_site)
            except (IndexError, UnicodeDecodeError):
                pass
            return response
    else:
        raise ImproperlyConfigured("Unsupported value for "
            "BACKLINKS_LOCAL_SITES: {!r}".format(BACKLINKS_LOCAL_SITES))
