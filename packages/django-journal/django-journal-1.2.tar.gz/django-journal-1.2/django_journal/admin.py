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
    list_display = ('time', '_tag', 'user', 'ip', 'html_message')
    list_filter = ('tag',)
    fields = ('time', 'tag', 'user', 'ip', 'html_message_no_filter')
    readonly_fields = fields
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
               .prefetch_related('objectdata_set__content_type',
                       'stringdata_set', 'objectdata_set__tag',
                       'stringdata_set__tag', 'objectdata_set__content_object')
        return qs

    def lookup_allowed(self, key, *args, **kwargs):
        return True

    def _tag(self, entry):
        name = entry.tag.name.replace(u'-', u'\u2011')
        return u'<a href="?tag__name="{0}">{0}</a>'.format(name)
    _tag.allow_tags = True
    _tag.short_description = _('Tag')

    def ip(self, entry):
        '''Search and return any associated stringdata whose tag is "ip"'''
        for stringdata in entry.stringdata_set.all():
            if stringdata.tag.name == 'ip':
                return stringdata.content
        return _('None')
    ip.short_description = _('IP')

    def user(self, entry):
        '''Search and return any associated objectdata whose tag is "user"'''
        for objectdata in entry.objectdata_set.all():
            if objectdata.tag.name == 'user':
                return self.object_filter_link(objectdata) + \
                        self.object_link(objectdata)
        return _('None')
    user.allow_tags = True
    user.short_description = _('User')

    def object_filter_link(self, objectdata):
        return u'<a href="?objectdata__content_type={0}&objectdata__object_id={1}">{2}</a>'.format(
                    objectdata.content_type_id,
                    objectdata.object_id,
                    objectdata.content_object)

    def object_link(self, obj_data):
        url = u'{0}:{1}_{2}_change'.format(self.admin_site.name,
                obj_data.content_type.app_label,
                obj_data.content_type.model)
        try:
            url = reverse(url, args=(obj_data.object_id,))
        except NoReverseMatch:
            return ''
        return u'<a href="{}" class="external-link"></a>'.format(url)

    def html_message_no_filter(self, entry):
        ctx = entry.message_context()
        for obj_data in entry.objectdata_set.all():
            key = obj_data.tag.name;
            ctx[key] = ctx[key] + self.object_link(obj_data)
        template = _(entry.template.content) # localize the template
        return u'<span>{}</span>'.format(template.format(**ctx))
    html_message_no_filter.allow_tags = True
    html_message_no_filter.short_description = _('Message')

    def html_message(self, entry):
        ctx = entry.message_context()
        for objectdata in entry.objectdata_set.all():
            key = objectdata.tag.name;
            ctx[key] = self.object_filter_link(objectdata) + \
                    self.object_link(objectdata)
        template = _(entry.template.content) # localize the template
        return u'<span>{}</span>'.format(template.format(**ctx))
    html_message.allow_tags = True
    html_message.short_description = _('Message')
    html_message.admin_order_field = 'message'

admin.site.register(Journal, JournalAdmin)
admin.site.register(Tag)
