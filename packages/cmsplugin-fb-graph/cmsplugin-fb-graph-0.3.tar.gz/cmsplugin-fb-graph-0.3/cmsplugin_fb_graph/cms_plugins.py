from urllib2 import URLError

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _

import facebook

import models
import settings


class CMSFBPlugin(CMSPluginBase):

    def get_facebook_data(self, instance, fql):
        try:
            auth_token = facebook.get_app_access_token(settings.FACEBOOK_APP_ID,
                                                       settings.FACEBOOK_APP_SECRET)
            graph = facebook.GraphAPI(auth_token)
            if instance.count > 0:
                limit = ' limit %s' % instance.count
            else:
                limit = ''
            fql += limit
            query = graph.fql(fql % {'uid': instance.user_id})
            return query
        except URLError:
            # Can't access facebook, return an empty response
            return []

    def render(self, context, instance, placeholder):
        context.update({
            'items': self.get_facebook_data(instance, self.fql),
            'instance': instance,
        })
        return context


class CMSFBAgendaPlugin(CMSFBPlugin):

    model = models.FBAgendaPlugin
    name = _('Facebook agenda')
    render_template = 'cmsplugin_fb_graph/agenda.html'
    fql = settings.EVENTS_FQL


class CMSFBNewsPlugin(CMSFBPlugin):

    model = models.FBNewsPlugin
    name = _('Facebook news')
    render_template = 'cmsplugin_fb_graph/news.html'
    fql = settings.NEWS_FQL

    def get_facebook_data(self, instance, fql):
        data = super(CMSFBNewsPlugin, self).get_facebook_data(instance, fql)
        return [elem for elem in data if elem['message']]

plugin_pool.register_plugin(CMSFBAgendaPlugin)
plugin_pool.register_plugin(CMSFBNewsPlugin)
