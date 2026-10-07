from django import forms

from .content import STRINGS


class ContactForm(forms.Form):
    name = forms.CharField(max_length=120)
    contact = forms.CharField(max_length=200)
    message = forms.CharField(max_length=4000, widget=forms.Textarea)
    # Honeypot: hidden from people with CSS + aria-hidden + tabindex=-1, but
    # naive spam bots fill every field they find. Non-empty → silently dropped.
    # Deliberately NOT named "website"/"url"/"company": browsers and password
    # managers autofill fields with such names, which would silently swallow
    # a real visitor's message.
    leave_empty = forms.CharField(required=False)

    def __init__(self, *args, lang="uz", **kwargs):
        super().__init__(*args, **kwargs)
        strings = STRINGS[lang]
        for field in self.fields.values():
            field.error_messages = {
                "required": strings["err_required"],
                "max_length": strings["err_too_long"],
            }

    @property
    def is_spam(self):
        return bool(self.data.get("leave_empty", "").strip())
