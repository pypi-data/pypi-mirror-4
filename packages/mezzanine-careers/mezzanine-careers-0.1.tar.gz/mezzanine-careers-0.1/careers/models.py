from django.db import models
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings
from mezzanine.core.models import Displayable, RichText, Ownable


class JobPost(Displayable, RichText):
    """
    A career job posting
    """

    class Meta:
        verbose_name = _("Job Post")
        verbose_name_plural = _("Job Posts")
        ordering = ("-publish_date",)

    @models.permalink
    def get_absolute_url(self):
        url_name = "jobpost_detail"
        kwargs = {"slug": self.slug}
        return (url_name, (), kwargs)

    def keyword_list(self):
        return getattr(self, "_keywords", self.keywords.all())

