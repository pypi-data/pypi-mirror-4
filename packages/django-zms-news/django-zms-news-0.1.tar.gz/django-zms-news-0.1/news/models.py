from django.db import models
from ckeditor.fields import RichTextField
from django.utils.translation import ugettext_lazy as _
from easy_thumbnails.fields import ThumbnailerImageField
from django.conf import settings
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
import datetime

class NewManager(models.Manager):
    def get_all(self):
        return self.all().order_by('-date')
    def get_active(self):
        return self.get_all().filter(active=True).exclude(date__gt=datetime.datetime.now())
    
class New(models.Model):
    slug = models.CharField(verbose_name=_(u"Slug"), unique=True, max_length=70)
    title = models.CharField(verbose_name=_(u"Title"),max_length=50)
    subtitle = models.CharField(verbose_name=_(u"Subtitle"),max_length=256, null=True) 
    resumen = models.TextField(verbose_name=_(u"Resumen"),null=True)
    text = RichTextField(verbose_name=_(u"Text"),null=True)    
    image = models.ImageField(verbose_name=_(u"Image"),upload_to = 'news', null=True, blank=True)
    date = models.DateTimeField(verbose_name=_(u"Date"),null=False)
    active = models.BooleanField(verbose_name=_(u"Active"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = NewManager()

    def __unicode__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        setattr(self, 'slug', slugify(getattr(self, 'title')))
        for lang_code, lang_verbose in settings.LANGUAGES:
            if hasattr(self, 'slug_%s' % lang_code) and hasattr(self, 'title_%s' % lang_code):
                if getattr(self, 'title_%s' % lang_code)!='':
                    setattr(self, 'slug_%s' % lang_code, slugify(getattr(self, 'title_%s' % lang_code, u"")))
                else:
                    setattr(self, 'slug_%s' % lang_code, slugify(getattr(self, 'title')))
        super(New, self).save(*args, **kwargs)
        
    def get_absolute_url(self):
        return reverse('news.views.new_detail', args=[str(self.id), str(self.slug)])

    
