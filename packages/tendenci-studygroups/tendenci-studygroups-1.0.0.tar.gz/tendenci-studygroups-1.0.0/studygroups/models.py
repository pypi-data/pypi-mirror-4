from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from tinymce import models as tinymce_models
from tendenci.apps.pages.models import BasePage
from tendenci.core.perms.object_perms import ObjectPermission
from studygroups.managers import StudyGroupManager
from studygroups.module_meta import StudyGroupMeta
from tendenci.apps.user_groups.models import Group


class StudyGroup(BasePage):
    """
    StudyGroups Plugin. Similar to Pages with extra fields.
    """

    mission = tinymce_models.HTMLField(null=True, blank=True)
    notes = tinymce_models.HTMLField(null=True, blank=True)
    contact_name = models.CharField(max_length=200, null=True, blank=True)
    contact_email = models.CharField(max_length=200, null=True, blank=True)
    join_link = models.CharField(max_length=200, null=True, blank=True)
    group = models.ForeignKey(Group)

    perms = generic.GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = StudyGroupManager()

    def __unicode__(self):
        return unicode(self.title)

    class Meta:
        permissions = (("view_studygroup", "Can view studygroup"),)

    @models.permalink
    def get_absolute_url(self):
        return ("studygroups.detail", [self.slug])

    def get_meta(self, name):
        """
        This method is standard across all models that are
        related to the Meta model.  Used to generate dynamic
        meta information niche to this model.
        """
        return StudyGroupMeta().get_meta(self, name)

    def officers(self):
        return Officer.objects.filter(study_group=self).order_by('pk')


class Position(models.Model):
    title = models.CharField(_(u'title'), max_length=200)

    def __unicode__(self):
        return unicode(self.title)


class Officer(models.Model):
    study_group = models.ForeignKey(StudyGroup)
    user = models.ForeignKey(User)
    position = models.ForeignKey(Position)
    phone = models.CharField(max_length=50, null=True, blank=True)

    def __unicode__(self):
        return "%s" % self.pk
