""""

Make url before admin:
    url(r'^admin/([^\/]+)/([^\/]+)/xls/$', 'feinheit.export.xls.admin_export_xls'),

Place a template named "change_list.html" in the appropriate admin template folder:
    /templates/admin/[app_name]/[model_name]/change_list.html

Use lowercase letters only.

The exporter supports very simplicistic elimination of duplicates too. Pass a
comma separated list of fieldnames as ``_exclude_duplicates`` if you only want
to export the first occurrence of combinations of field values.

::

    {% extends 'admin/change_list.html' %}{% load i18n %}
    {% block object-tools %}
    <ul class="object-tools">
      {% if has_add_permission %}
      <li>
        <a href="add/{% if is_popup %}?_popup=1{% endif %}" class="addlink">
          {% blocktrans with cl.opts.verbose_name as name %}Add {{ name }}{% endblocktrans %}
        </a>
      </li>
      {% endif %}
    <li><a href="xls/?{{ request.GET.urlencode }}" class="viewsitelink">XLS</a></li>
    <li><a href="xls/?{{ request.GET.urlencode }}&amp;_exclude_duplicates=field1,field2" class="viewsitelink">XLS (no dups)</a></li>
    </ul>
    {% endblock %}


"""

import xlwt, StringIO

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse


@staff_member_required
def admin_export_xls(request, app, model):
    mc = ContentType.objects.get(app_label=app, model=model).model_class()
    wb = xlwt.Workbook()
    ws = wb.add_sheet(unicode(mc._meta.verbose_name_plural))
    ws.write(0,0, 'unicode')
    for i, f in enumerate(mc._meta.fields):
        ws.write(0,i+1, f.name)

    exclude_dup = request.GET.get('_exclude_duplicates', u'')
    if exclude_dup:
        exclude_dup = exclude_dup.split(',')
    seen = set()

    qs = mc.objects.filter(**dict(
        (k, v) for k, v in request.GET.items() if k not in ('p', '_exclude_duplicates')
        )).select_related()

    ri = 0
    for row in qs:
        if ri >= 2**16 - 2:
            ws.write(ri+1, 0, 'TRUNCATED, cannot export more than 65535 rows')
            break

        if exclude_dup:
            this = tuple(getattr(row, f, None) for f in exclude_dup)
            if this in seen:
                continue
            seen.add(this)

        ws.write(ri+1, 0, unicode(row))
        for ci, f in enumerate(mc._meta.fields):
            if f.choices:
                ws.write(ri+1, ci+1, unicode(getattr(row, 'get_%s_display' % f.name)()))
            else:
                ws.write(ri+1, ci+1, unicode(getattr(row, f.name)))

        ri += 1

    output = StringIO.StringIO()
    wb.save(output)
    response = HttpResponse(output.getvalue(), mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s.xls' % \
          (unicode(mc._meta.verbose_name_plural),)
    return response
