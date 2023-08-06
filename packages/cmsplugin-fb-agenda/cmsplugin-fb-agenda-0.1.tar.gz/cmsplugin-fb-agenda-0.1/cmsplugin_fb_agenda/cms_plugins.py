from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _

import facebook

import models
import settings


class CMSFBAgendaPlugin(CMSPluginBase):

    model = models.FBAgendaPlugin
    name = _('Facebook agenda')
    render_template = 'cmsplugin_fb_agenda/agenda.html'

    def get_facebook_data(self, instance):
        auth_token = facebook.get_app_access_token(settings.FACEBOOK_APP_ID,
                                                   settings.FACEBOOK_APP_SECRET)
        graph = facebook.GraphAPI(auth_token)
        query = graph.fql(settings.EVENTS_FQL % instance.user_id)
        return query

    def render(self, context, instance, placeholder):
        context.update({
            'events': self.get_facebook_data(instance),
            'instance': instance,
        })
        return context


plugin_pool.register_plugin(CMSFBAgendaPlugin)
