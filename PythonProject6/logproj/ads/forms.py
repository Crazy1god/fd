from django import forms
from .models import Ad, Complaint, AdMessage

class AdForm(forms.ModelForm):
    submit_for_moderation = forms.BooleanField(required=False, initial=True, label="Submit for moderation")

    class Meta:
        model = Ad
        fields = ["title", "description", "price", "currency", "category", "city"]

class ModerationDecisionForm(forms.Form):
    approve = forms.BooleanField(required=False)
    comment = forms.CharField(required=False, widget=forms.Textarea)

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["reason", "text"]

class MessageForm(forms.ModelForm):
    class Meta:
        model = AdMessage
        fields = ["text"]