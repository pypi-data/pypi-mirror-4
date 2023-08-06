import csv

from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse

def export_as_csv(modeladmin, request, queryset):
    """
    CSV export for journal
    """
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=journal.csv'
    writer = csv.writer(response)

    writer.writerow(['time', 'tag', 'message'])
    for journal in queryset:
        row = [
                journal.time.isoformat(' '),
                journal.tag.name.encode('utf-8'),
                unicode(journal).encode('utf-8'),
              ]
        writer.writerow(row)
    return response
export_as_csv.short_description = _(u"Export CSV file")
