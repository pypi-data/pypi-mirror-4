import django.contrib.admin as admin

from models import Journal, Tag, ObjectData, StringData

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse, NoReverseMatch

class ObjectDataInlineAdmin(admin.TabularInline):
    model = ObjectData
    fields = ('tag', 'content_type', 'content_object')
    readonly_fields = fields
    extra = 0
    max_num = 0

class StringDataInlineAdmin(admin.TabularInline):
    model = StringData
    fields = ('tag', 'content')
    readonly_fields = fields
    extra = 0
    max_num = 0

class JournalAdmin(admin.ModelAdmin):
    list_display = ('time', 'tag', 'html_message')
    list_filter = ('tag',)
    fields = list_display
    readonly_fields = list_display
    inlines = (
            ObjectDataInlineAdmin, 
            StringDataInlineAdmin,
    )
    date_hierarchy = 'time'
    search_fields = ('message','tag__name','time')

    class Media:
        css = {
                'all': ('journal/css/journal.css',),
        }

    def queryset(self, request):
        '''Get as much data as possible using the fewest requests possible.'''
        qs = super(JournalAdmin, self).queryset(request)
        qs = qs.select_related('tag', 'template') \
               .prefetch_related('objectdata_set__content_type', 'stringdata_set',
                       'objectdata_set__tag')
        return qs

    def lookup_allowed(self, key, *args, **kwargs):
        return True

    def object_link(self, obj_data):
        url = '{0}:{1}_{2}_change'.format(self.admin_site.name,
                obj_data.content_type.app_label,
                obj_data.content_type.model)
        #try:
        url = reverse(url, args=(obj_data.object_id,))
        #except NoReverseMatch:
        #    return ''
        return '<a href="%s" class="external-link"></a>' % url

    def html_message(self, entry):
        import pdb
        pdb.set_trace()
        ctx = entry.message_context()
        for obj_data in entry.objectdata_set.select_related():
            content_type_id = obj_data.content_type.pk;
            object_id = obj_data.object_id;
            key = obj_data.tag.name;
            ctx[key] = '<a href="?objectdata__content_type={0}&objectdata__object_id={1}">{2}{3}</a>'.format(
                    content_type_id, object_id, ctx[key], self.object_link(obj_data))
        template = _(entry.template_content) # localize the template
        return '<span>{}</span>'.format(template.format(**ctx))
    html_message.allow_tags = True
    html_message.short_description = _('Message')
    html_message.admin_order_field = 'message'

admin.site.register(Journal, JournalAdmin)
admin.site.register(Tag)
