from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe


class SearchForm(forms.Form):
	SEARCH_ENTRY = 1
	SEARCH_USER = 2
	SEARCH_CHOICES = (
		(SEARCH_ENTRY, 'Articles'),
		(SEARCH_USER, 'Users'),
	)
	
	q = forms.CharField(widget=forms.TextInput(attrs={'id':'ajaxsearch', 'class':'ajaxsearchmain', 'placeholder':'Search articles and users'}), required=False)
	choice=forms.ChoiceField(widget=forms.Select(attrs={'id':'ajaxsearchchoicefield', 'class':'ajaxsearchchoice'}), choices=SEARCH_CHOICES, initial=SEARCH_INITIAL)
