from calendar import month_name
from django.shortcuts import get_object_or_404
from collections import defaultdict
from django.contrib.contenttypes.models import ContentType
from django import VERSION

from careers.models import JobPost
from mezzanine.conf import settings
from mezzanine.generic.models import AssignedKeyword, Keyword
from mezzanine.utils.views import render, paginate


def jobpost_list(request, tag=None, year=None, month=None, template="careers/jobpost_list.html"):
    """
    Display a list of job posts that are filtered by year, month.
    """
    settings.use_editable()
    templates = []
    jobposts = JobPost.objects.published()
    if tag is not None:
        tag = get_object_or_404(Keyword, slug=tag)
        jobposts = jobposts.filter(keywords__in=tag.assignments.all())
    if year is not None:
        jobposts = jobposts.filter(publish_date__year=year)
        if month is not None:
            jobposts = jobposts.filter(publish_date__month=month)
            month = month_name[int(month)]
    # We want to iterate keywords and categories for each blog post
    # without triggering "num posts x 2" queries.
    #
    # For Django 1.3 we create dicts mapping blog post IDs to lists of
    # categories and keywords, and assign these to attributes on each
    # blog post. The Blog model then uses accessor methods to retrieve
    # these attributes when assigned, which will fall back to the real
    # related managers for Django 1.4 and higher, which will already
    # have their data retrieved via prefetch_related.

    jobposts = jobposts.select_related("user")
    if VERSION >= (1, 4):
        jobposts = jobposts.prefetch_related("keywords__keyword")
    else:
        if jobposts:
            ids = ",".join([str(p.id) for p in jobposts])
        keywords = defaultdict(list)
        jobpost_type = ContentType.objects.get(app_label="careers", model="jobpost")
        assigned = AssignedKeyword.objects.filter(jobpost__in=jobposts, content_type=jobpost_type).select_related("keyword")
        for a in assigned:
            keywords[a.object_pk].append(a.keyword)
        for i, post in enumerate(jobposts):
            setattr(jobposts[i], "_keywords", keywords[post.id])
    jobposts = paginate(jobposts, request.GET.get("page", 1),
                          settings.CAREERS_PER_PAGE,
                          settings.MAX_PAGING_LINKS)
    context = {"jobposts": jobposts, "year": year, "month": month, "tag": tag}
    templates.append(template)
    return render(request, templates, context)


def jobpost_detail(request, slug, year=None, month=None, day=None, template="careers/jobpost_detail.html"):
    """. Custom templates are checked for using the name
    ``careers/jobpost_detail_XXX.html`` where ``XXX`` is the job
    posts's slug.
    """
    jobposts = JobPost.objects.published()
    jobpost = get_object_or_404(jobposts, slug=slug)
    context = {"jobpost": jobpost, "editable_obj": jobpost}
    templates = [u"careers/jobpost_detail_%s.html" % unicode(slug), template]
    return render(request, templates, context)

