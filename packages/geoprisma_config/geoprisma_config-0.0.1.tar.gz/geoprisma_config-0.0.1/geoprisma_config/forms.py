from django import forms
from geoprisma_config.models import *
from geoprisma_config.widgets import MyTextInput

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        widgets = {
            'name': MyTextInput(), 
            'source': MyTextInput(), 
            }
        
class ServiceOptionForm(forms.ModelForm):
    class Meta:
        model = ServiceOption
        widgets = {
            'name': MyTextInput(), 
            'value': MyTextInput(), 
            }

class DatastoreForm(forms.ModelForm):
    class Meta:
        model = Datastore
        widgets = {
            'name': MyTextInput(), 
            'layers': MyTextInput(), 
            }
        
class DatastoreOptionForm(forms.ModelForm):
    class Meta:
        model = DatastoreOption
        widgets = {
            'name': MyTextInput(), 
            'value': MyTextInput(), 
            }

class FieldForm(forms.ModelForm):
    class Meta:
        model = Field
        widgets = {
            'name': MyTextInput(), 
            'title': MyTextInput(), 
            'key': MyTextInput(), 
            'domain': MyTextInput(), 
            }
        
class FieldOptionForm(forms.ModelForm):
    class Meta:
        model = FieldOption
        widgets = {
            'name': MyTextInput(), 
            'value': MyTextInput(), 
            }

class AccessFilterForm(forms.ModelForm):
    class Meta:
        model = AccessFilter
        widgets = {
            'name': MyTextInput(), 
            }
        
class AccessFilterOptionForm(forms.ModelForm):
    class Meta:
        model = AccessFilterOption
        widgets = {
            'name': MyTextInput(), 
            'value': MyTextInput(), 
            }

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        widgets = {
            'name': MyTextInput(),
            'aclName': MyTextInput(), 
            'key': MyTextInput(), 
            'domain': MyTextInput(), 
            }

class ResourceOptionForm(forms.ModelForm):
    class Meta:
        model = ResourceOption
        widgets = {
            'name': MyTextInput(), 
            'value': MyTextInput(), 
            'key': MyTextInput(),
            'domain': MyTextInput(), 
            }

class WidgetForm(forms.ModelForm):
    class Meta:
        model = Widget
        widgets = {
            'name': MyTextInput(), 
            }

class WidgetOptionForm(forms.ModelForm):
    class Meta:
        model = WidgetOption
        widgets = {
            'name': MyTextInput(), 
            'value': MyTextInput(), 
            }

class MapContextForm(forms.ModelForm):
    class Meta:
        model = MapContext
        widgets = {
            'name': MyTextInput(), 
            }

class MapContextOptionForm(forms.ModelForm):
    class Meta:
        model = MapContextOption
        widgets = {
            'name': MyTextInput(), 
            'value': MyTextInput(), 
            }

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        widgets = {
            'name': MyTextInput(), 
            'template': MyTextInput(), 
            }

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        widgets = {
            'name': MyTextInput(), 
            }
