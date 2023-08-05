from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import register_setting


register_setting(
    name="jobpostS_PER_PAGE",
    label=_("Job Posts per page"),
    description=_("Number of job posts shown on a career listing page."),
    editable=True,
    default=7,
)

register_setting(
    name="jobpost_SLUG",
    description=_("Slug of the page object for the careers app."),
    editable=False,
    default="jobpost",
)
