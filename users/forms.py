from django.contrib.auth.forms import (
    AuthenticationForm as BaseAuthenticationForm,
    SetPasswordForm as BaseSetPasswordForm,
    PasswordChangeForm as BasePasswordChangeForm,
    PasswordResetForm,
)

import re, os
from users.models import CustomUser
from django.utils.translation import gettext_lazy as _


class SetPasswordForm(BaseSetPasswordForm):
    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")

        if not re.findall("\d", new_password1):
            self.add_error(
                "new_password1", _("The password must contain at least one digit, 0-9.")
            )

        if not re.findall("[A-Z]", new_password1):
            self.add_error(
                "new_password1",
                _("The password must contain at least 1 uppercase letter, A-Z."),
            )

        if not re.findall("[a-z]", new_password1):
            self.add_error(
                "new_password1",
                _("The password must contain at least 1 lowercase letter, a-z."),
            )

        if not re.findall("[~!@#$%^&*_]", new_password1):
            self.add_error(
                "new_password1",
                _("The password must contain at least 1 symbol: ~!@#$%^&*_"),
            )

        return cleaned_data
    
    
    def save(self, commit=True):
        user = super().save(commit)
        user.is_active = True
        user.save()
        return user
    
    
    
class PasswordChangeForm(BasePasswordChangeForm, SetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        BasePasswordChangeForm.__init__(self, user, *args, **kwargs)
        SetPasswordForm.__init__(self, user, *args, **kwargs)