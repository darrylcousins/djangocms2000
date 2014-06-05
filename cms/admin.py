from django.contrib import admin
from django.contrib.contenttypes import generic
from django import forms
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.test.client import Client

import settings as cms_settings
from forms import PageForm, ReadonlyInput
from models import Page, Block, Image, MenuItem

class BlockForm(forms.ModelForm):
    class Meta:
        model = Block
    def __init__(self, *args, **kwargs):
        super(BlockForm, self).__init__(*args, **kwargs)

        # change the raw_content widget based on the format of the block - a bit hacky but best we can do
        if 'instance' in kwargs:
            self.fields['raw_content'].widget.attrs['class'] = "%s cms cms-%s" % (self.fields['raw_content'].widget.attrs['class'], kwargs['instance'].format)
        
        required_cb = cms_settings.BLOCK_REQUIRED_CALLBACK
        if callable(required_cb) and 'instance' in kwargs:
            self.fields['raw_content'].required = required_cb(kwargs['instance'])
        

class BlockFormSet(generic.generic_inlineformset_factory(Block)):
    def __init__(self, *args, **kwargs):
        super(BlockFormSet, self).__init__(*args, **kwargs)
        self.can_delete = cms_settings.ADMIN_CAN_DELETE_BLOCKS


class BlockInline(generic.GenericTabularInline):
    model = Block
    extra = 0
    formset = BlockFormSet
    fields = ('raw_content',)
    form = BlockForm




class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
    def __init__(self, *args, **kwargs):
        super(ImageForm, self).__init__(*args, **kwargs)

        required_cb = cms_settings.IMAGE_REQUIRED_CALLBACK
        if callable(required_cb) and 'instance' in kwargs:
            self.fields['file'].required = required_cb(kwargs['instance'])
        


class ImageInline(generic.GenericTabularInline):
    model = Image
    extra = 0
    exclude = ('label',)
    form = ImageForm

class CMSBaseAdmin(admin.ModelAdmin):
    inlines=[BlockInline,ImageInline,]
    list_display=['get_title',]
    save_on_top = True
    class Media:
        js = cms_settings.ADMIN_JS
        css = cms_settings.ADMIN_CSS
    class Meta:
        abstract=True
        
    def save_model(self, request, obj, form, change):
        '''Save model, then add blocks/images via dummy rendering.
           
           NOTE: This will naively attempt to render the page using the 
           *current*  django Site object, so if you're in the admin of one site
           editing pages on another, the dummy render will silently fail.
        
        '''
        returnval = super(CMSBaseAdmin, self).save_model(request, obj, form, change)
        
        if getattr(obj, 'get_absolute_url', None):
            c = Client()
            response = c.get(unicode(obj.get_absolute_url()), 
                             {'cms_dummy_render': cms_settings.SECRET_KEY},
                             HTTP_COOKIE='')
        return returnval


class PageAdmin(CMSBaseAdmin):
    list_display=['page_title', 'url', 'template', 'is_live', 'creation_date', 'view_on_site',]
    list_display_links=['page_title', 'url', ]

    list_filter=['site', 'template', 'is_live', 'creation_date',]
    
    def view_on_site(self, instance):
        return '<a href="%s" target="_blank">view page</a>' % (instance.get_absolute_url())
    view_on_site.allow_tags = True
    view_on_site.short_description = ' '
    
    
    search_fields = ['url', 'blocks__compiled_content', 'template',]
    form = PageForm
    exclude = []
    
    
if cms_settings.USE_SITES_FRAMEWORK:
    PageAdmin.list_display.append('site')
else:
    PageAdmin.exclude.append('site')
        
admin.site.register(Page, PageAdmin)


admin.site.register(MenuItem, list_display=['__unicode__','page','sort'])






# Block/Image admin - restrict to just "site" blocks to avoid confusing the user
# Note - end users should only be given change permissions on these

class BlockFormSite(BlockForm):
    label = forms.CharField(widget=ReadonlyInput)

class BlockAdmin(admin.ModelAdmin):
    def queryset(self, request):
        if False and request.user.is_superuser:
            return Block.objects.all()
        else:
            return Block.objects.filter(content_type=ContentType.objects.get_for_model(Site))

    form = BlockFormSite
    fields = ['label', 'raw_content',]
    list_display = ['label_display', 'format', 'content_display',]
    search_fields = ['label', ]

    class Media:
        js = cms_settings.ADMIN_JS
        css = cms_settings.ADMIN_CSS

if cms_settings.USE_SITES_FRAMEWORK:
    BlockAdmin.list_display.append('content_object')

admin.site.register(Block, BlockAdmin)


class ImageFormSite(forms.ModelForm):
    class Meta:
        model = Image
    label = forms.CharField(widget=ReadonlyInput)

class ImageAdmin(admin.ModelAdmin):
    def queryset(self, request):
        if False and request.user.is_superuser:
            return Image.objects.all()
        else:
            return Image.objects.filter(content_type=ContentType.objects.get_for_model(Site))

    fields = ['label', 'file', 'description', ]
    list_display = ['label_display',]
    form = ImageFormSite
    search_fields = ['label', ]

if cms_settings.USE_SITES_FRAMEWORK:
    ImageAdmin.list_display.append('content_object')

admin.site.register(Image, ImageAdmin)
