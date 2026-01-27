from django import forms
from django.contrib import admin
from members.models.slackinvitesetup import SlackInvitationSetup
import pyotp


class SlackInvitationSetupForm(forms.ModelForm):
    admin_password = forms.CharField(
        label="Slack Admin Password",
        required=False,
        widget=forms.PasswordInput(render_value=True),
        help_text="Password for the Slack admin user (will be encrypted). Leave blank to keep unchanged.",
    )

    totp_secret = forms.CharField(
        label="Slack Admin TOTP Secret",
        required=False,
        widget=forms.PasswordInput(render_value=True),
        help_text="TOTP secret for Slack admin 2FA (will be encrypted). Leave blank to keep unchanged.",
    )

    class Meta:
        model = SlackInvitationSetup
        fields = [
            "invite_url",
            "emails",
            "admin_username",
            "admin_password",
            "totp_secret",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["admin_password"].initial = self.instance.admin_password
            self.fields["totp_secret"].initial = self.instance.totp_secret

    def save(self, commit=True):
        instance = super().save(commit=False)
        pwd = self.cleaned_data.get("admin_password")
        if pwd:
            instance.admin_password = pwd
        elif self.instance and self.instance.pk:
            # Keep existing password if left blank
            instance.admin_password_encrypted = self.instance.admin_password_encrypted

        totp = self.cleaned_data.get("totp_secret")
        if totp:
            instance.totp_secret = totp
        elif self.instance and self.instance.pk:
            # Keep existing secret if left blank
            instance.totp_secret_encrypted = self.instance.totp_secret_encrypted
        if commit:
            instance.save()
        return instance



class SlackInvitationSetupAdmin(admin.ModelAdmin):
    form = SlackInvitationSetupForm
    list_display = ("id", "invite_url", "updated_at", "updated_by")
    readonly_fields = ("updated_at", "updated_by", "current_totp_code")

    def current_totp_code(self, obj):
        secret = obj.totp_secret
        if secret:
            try:
                return pyotp.TOTP(secret).now()
            except Exception as e:
                return f"[TOTP error: {e}]"
        return "(ingen secret)"
    current_totp_code.short_description = "Aktuel TOTP-kode (6 cifre)"

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
