from django import forms
from django.contrib import admin, messages
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html
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
    list_display = ("id", "admin_invite_url_link", "updated_at", "updated_by")

    def admin_invite_url_link(self, obj):
        url = f"/admin/members/slackinvitationsetup/{obj.pk}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.invite_url)
    admin_invite_url_link.short_description = "Slack Admin Invite URL"
    actions = ["calculate_totp_code_action"]

    def calculate_totp_code_action(self, request, queryset):
        for obj in queryset:
            secret = obj.totp_secret
            if secret:
                try:
                    totp_code = pyotp.TOTP(secret).now()
                except Exception as e:
                    totp_code = f"[TOTP error: {e}]"
            else:
                totp_code = "(ingen secret)"
            self.message_user(
                request, f"TOTP-kode for '{obj}': {totp_code}", level=messages.INFO
            )
            ct = ContentType.objects.get_for_model(self.model)
            LogEntry.objects.create(
                user_id=request.user.pk,
                content_type=ct,
                object_id=obj.pk,
                object_repr=str(obj),
                action_flag=CHANGE,
                change_message="Requested TOTP code via admin action.",
            )

    calculate_totp_code_action.short_description = (
        "Beregn og vis TOTP-kode for valgte opsætninger"
    )

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
