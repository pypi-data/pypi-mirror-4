from django.db import models
from conf.types import *# Create an abstract class for the new manager.

class Service(models.Model):
    name = models.CharField(max_length=255, unique=True)
    source = models.TextField()
    type = models.PositiveIntegerField(choices=SERVICE_TYPES)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

class ServiceOption(models.Model):
    service = models.ForeignKey(Service)
    name = models.TextField()
    value = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name
    
class Datastore(models.Model):
    service = models.ForeignKey(Service)
    name = models.CharField(max_length=255, unique=True)
    layers = models.TextField(null=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name
    
class DatastoreOption(models.Model):
    datastore = models.ForeignKey(Datastore)
    name = models.TextField()
    value = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

class Field(models.Model):
    name = models.CharField(max_length=255, unique=True)
    title = models.TextField(blank=True)
    key = models.TextField(null=True, blank=True)
    domain = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

class FieldOption(models.Model):
    field = models.ForeignKey(Field)
    name = models.TextField()
    value = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

class AccessFilter(models.Model):
    name = models.CharField(max_length=255, unique=True)


    def __unicode__(self):
        return self.name

class AccessFilterOption(models.Model):
    accessfilter = models.ForeignKey(AccessFilter)
    name = models.TextField()
    value = models.TextField(null=True, blank=True)


    def __unicode__(self):
        return self.name

class Resource(models.Model):
    name = models.CharField(max_length=255, unique=True)
    aclName = models.TextField(null=True, blank=True, db_column='acl_name')
    key = models.TextField(null=True, blank=True)
    domain = models.TextField(null=True, blank=True)
    datastores = models.ManyToManyField(Datastore)
    accessfilters = models.ManyToManyField(AccessFilter, null=True, blank=True)
    models.ManyToManyField(Field, through='ResourceField')

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

class ResourceField(models.Model):
    resource = models.ForeignKey(Resource)
    field = models.ForeignKey(Field)
    order = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ('order',)

    def save(self, *args, **kwargs):
        model = self.__class__

        if self.order is None:
            # Append
            try:
                last = model.objects.filter(resource=self.resource).order_by('-order')[0]
                self.order = last.order + 1
            except IndexError:
                # First row
                self.order = 1
                
        return super(ResourceField, self).save(*args, **kwargs)


    def __unicode__(self):
        return self.field.name

class ResourceOption(models.Model):
    resource = models.ForeignKey(Resource)
    name = models.TextField()
    value = models.TextField(null=True, blank=True)
    key = models.TextField(null=True, blank=True)
    domain = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

class Widget(models.Model):
    name = models.CharField(max_length=255, unique=True)
    type = models.PositiveIntegerField(choices=WIDGET_TYPES)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

class WidgetOption(models.Model):
    widget = models.ForeignKey(Widget)
    name = models.TextField()
    value = models.TextField(null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ('order',)

    def save(self, *args, **kwargs):
        model = self.__class__

        if self.order is None:
            # Append
            try:
                last = model.objects.filter(widget=self.widget).order_by('-order')[0]
                self.order = last.order + 1
            except IndexError:
                # First row
                self.order = 1
                
        return super(WidgetOption, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

class MapContext(models.Model):
    name = models.CharField(max_length=255, unique=True)
    models.ManyToManyField(Resource, through='MapContextResource')

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name
    
class MapContextOption(models.Model):
    mapContext = models.ForeignKey(MapContext, db_column='mapcontext_id')
    name = models.TextField()
    value = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

class MapContextResource(models.Model):
    mapContext = models.ForeignKey(MapContext, db_column='mapcontext_id')
    resource = models.ForeignKey(Resource)
    order = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ('order',)

    def save(self, *args, **kwargs):
        model = self.__class__

        if self.order is None:
            # Append
            try:
                last = model.objects.filter(mapContext=self.mapContext).order_by('-order')[0]
                self.order = last.order + 1
            except IndexError:
                # First row
                self.order = 1
                
        return super(MapContextResource, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.resource.name

class Application(models.Model):
    name = models.CharField(max_length=255, unique=True)
    template = models.TextField()
    type = models.PositiveIntegerField(choices=APPLICATION_TYPES)
    models.ManyToManyField(Widget, through='ApplicationWidget')

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name
    
class ApplicationWidget(models.Model):
    application = models.ForeignKey(Application)
    widget = models.ForeignKey(Widget)
    order = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ('order',)

    def save(self, *args, **kwargs):
        model = self.__class__

        if self.order is None:
            # Append
            try:
                last = model.objects.filter(application=self.application).order_by('-order')[0]
                self.order = last.order + 1
            except IndexError:
                # First row
                self.order = 1
                
        return super(ApplicationWidget, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.widget.name

class Session(models.Model):
    name = models.CharField(max_length=255, unique=True)
    application = models.ForeignKey(Application)
    mapContext = models.ForeignKey(MapContext, db_column='mapcontext_id')

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name
