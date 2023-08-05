# -*- coding: utf-8 -*-

"""
:copyright: (c) 2012 by the dot2code Team, see AUTHORS.txt for more details.
:license: GPL, see LICENSE.txt for more details.
"""

from __future__ import absolute_import
from django.db import models
from django.utils.translation import ugettext_lazy as _
from varnish_bans_manager.core.models.base import Model, RevisionField
from varnish_bans_manager.core.models.group import Group
from varnish_bans_manager.core.helpers.cli import Varnish


class Cache(Model):
    VERSION_21 = 21
    VERSION_30 = 30
    VERSION_CHOICES = (
        (VERSION_21, '2.1'),
        (VERSION_30, '>= 3.0'),
    )

    name = models.CharField(
        _('Name'),
        help_text=_('Some name used internally by VBM to refer to the caching node. If not provided, the host and port number of the node will be used.'),
        max_length=255,
        null=True,
        blank=True
    )
    host = models.CharField(
        _('Host'),
        help_text=_('Name or IP address of the server running the Varnish caching node.'),
        max_length=255,
        null=False
    )
    port = models.PositiveIntegerField(
        _('Port'),
        help_text=_('Varnish management port number.'),
        null=False
    )
    secret = models.TextField(
        _('Secret'),
        help_text=_('If the -S secret-file is used in the caching node, provide here the contents of that file in order to authenticate CLI connections opened by VBM.'),
        max_length=65536,
        null=True,
        blank=True,
    )
    version = models.SmallIntegerField(
        _('Version'),
        help_text=_('Select the Varnish version running in the caching node.'),
        choices=VERSION_CHOICES,
        default=VERSION_30,
        null=False
    )
    weight = models.SmallIntegerField(
        default=0,
        null=False
    )
    group = models.ForeignKey(
        Group,
        related_name='caches',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    revision = RevisionField()
    created_at = models.DateTimeField(
        auto_now_add=True,
        null=False
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        null=False
    )

    def _human_name(self):
        return self.name if self.name else '%s:%d' % (self.host, self.port,)

    human_name = property(_human_name)

    def ban(self, expression):
        self._cli('ban', expression)

    def ban_list(self):
        return self._cli('ban_list')

    def _cli(self, name, *args):
        varnish = Varnish(
            self.host, int(self.port), self.human_name,
            secret=self.secret,
            version=self.version)
        try:
            return getattr(varnish, name)(*args)
        finally:
            varnish.quit()

    class Meta:
        app_label = 'core'
