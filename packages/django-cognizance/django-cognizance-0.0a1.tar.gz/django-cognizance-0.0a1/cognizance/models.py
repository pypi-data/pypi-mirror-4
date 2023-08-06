from django.db import models 
from django.utils.html import strip_tags, linebreaks
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
from uuid import uuid4
from django.forms import ModelForm
from django.contrib.auth.models import User, Group
from django.db.models import Max

# non-standard imports
from uuslug import uuslug

STATUSES = (
    ('Idea', _('idea')),
    ('Published', _('published')),
)

class EntryVersion(models.Model):
    version         = models.IntegerField(null=True, blank=True)
    uid             = models.CharField(max_length=36)
    title           = models.CharField(max_length=100)
    slug            = models.CharField(max_length=100)
    content         = models.TextField(_('content'), blank=True)
    created         = models.DateTimeField(null=True, blank=True)
    start_date      = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return "%s - %s" % (self.version, self.title)

    def bump_version(self, uid):
        highest_version = EntryVersion.objects.filter(uid=uid).aggregate(Max('version'))['version__max']
        if highest_version == None:
            return 0
        else: 
            return highest_version + 1

    def save(self, *args, **kwargs):
        self.version = self.bump_version(self.uid)
        self.start_date = datetime.now()
        super(EntryVersion, self).save(*args, **kwargs)

class Entry(models.Model):
    author          = models.ForeignKey(User)
    title           = models.CharField(max_length=100)
    slug            = models.CharField(max_length=100, null=True, blank=True)
    created         = models.DateTimeField(null=True, blank=True)
    uid             = models.CharField(max_length=36, null=True, blank=True)
    modified        = models.DateTimeField(null=True, blank=True)
    start_date      = models.DateTimeField(null=True, blank=True)
    content         = models.TextField(_('content'), blank=True)
    comments_on     = models.BooleanField(default=True)
    comment_count   = models.IntegerField(default=0, null=True, blank=True)
    excerpt         = models.CharField(max_length=250, null=True, blank=True)
    views           = models.IntegerField(default=0, null=True, blank=True)
    versions        = models.IntegerField(default=0, null=True, blank=True)
    calculated_score= models.DecimalField(max_digits=5, decimal_places=5, null=True, blank=True)
    
    class Meta:
        ordering = ['-created']
        verbose_name_plural = _('entries')

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if len(self.content) > 200:
            self.excerpt        = "%s..." % (self.content[0:200])
        else:
            self.excerpt        = self.content

        if not self.id:
            self.created        = datetime.now()
            self.slug           = uuslug(self.title, instance=self)
            self.uid            = str(uuid4())           
        else:
            self.modified = datetime.now()

        # Will want to move this out to a signal to keep the model clean.
        version             = EntryVersion()
        version.title       = self.title
        version.uid         = self.uid
        version.slug        = self.slug
        version.start_date  = self.start_date
        version.save()
        super(Entry, self).save(*args, **kwargs)

class EntryForm(ModelForm):
    class Meta:
        model = Entry
        exclude = (
            'author', 'created', 'comment_count', 'excerpt', 'modified', 
            'views', 'versions', 'slug', 'uid', 'calculated_scores',
        )
