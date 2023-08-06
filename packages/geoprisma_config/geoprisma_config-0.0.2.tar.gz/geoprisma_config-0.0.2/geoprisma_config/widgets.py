from django import forms

class MyTextInput(forms.TextInput):

    def __init__(self):
        super(MyTextInput,self).__init__(attrs={'size':'50'})
