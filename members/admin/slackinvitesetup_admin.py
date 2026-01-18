from django import forms
from django.contrib import admin
from members.models.slackinvitesetup import SlackInvitationSetup


class SlackInvitationSetupForm(forms.ModelForm):
    admin_password = forms.CharField(
        label="Slack Admin Password",
        required=False,
        widget=forms.PasswordInput(render_value=True),
        help_text="Password for the Slack admin user (will be encrypted). Leave blank to keep unchanged.",
    )

    class Meta:
        model = SlackInvitationSetup
        fields = [
            "invite_url",
            "emails",
            "admin_username",
            "admin_password",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["admin_password"].initial = self.instance.admin_password

    def save(self, commit=True):
        instance = super().save(commit=False)
        pwd = self.cleaned_data.get("admin_password")
        if pwd:
            instance.admin_password = pwd
        elif self.instance and self.instance.pk:
            # Keep existing password if left blank
            instance.admin_password_encrypted = self.instance.admin_password_encrypted
        if commit:
            instance.save()
        return instance


class SlackInvitationSetupAdmin(admin.ModelAdmin):
    form = SlackInvitationSetupForm
    list_display = ("invite_url", "updated_at", "updated_by")
    readonly_fields = ("updated_at", "updated_by")

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
