from cms.models import CMSPlugin
from django.db import models
from django.utils.translation import ugettext_lazy as _


class FBAgendaPlugin(CMSPlugin):

    user_id = models.CharField(max_length=32)

    def __unicode__(self):
        return _(u'fb agenda for %(user_id)s') % {'user_id': self.user_id}
