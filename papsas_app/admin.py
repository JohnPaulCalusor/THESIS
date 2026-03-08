from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.hashers import make_password
from exponent_server_sdk import (
    PushClient,
    PushMessage,
    DeviceNotRegisteredError,
    PushServerError,
)
import logging

from .models import (
    User,
    MembershipTypes,
    Vote,
    Candidacy,
    Officer,
    Election,
    Event,
    EventRegistration,
    UserMembership,
    Venue,
    Attendance,
    NewsandOffers,
    Achievement,
    EventRating,
    DevicePushToken,
    RegionalPost,
    RegionalVideo,
    RegionalOfficer,
)
from .models_position import Position


class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "username", "email_verified")
    search_fields = ["id__icontains", "email"]

    # disables admin to change anything
    # readonly_fields = ('password',)

    def save_model(self, request, obj, form, change):
        if "password" in form.changed_data:
            obj.password = make_password(obj.password)  # Hash the password
        super().save_model(request, obj, form, change)


class EventRegistrationAdmin(admin.ModelAdmin):
    search_fields = ["id__icontains", "user__email"]


class UserMembershipAdmin(admin.ModelAdmin):
    search_fields = ["id__icontains", "user__email"]


class ElectionAdminForm(forms.ModelForm):
    class Meta:
        model = Election
        fields = "__all__"
        label_suffix = ""
        labels = {
            "numWinners": "At-large winner cap (leave blank/zero to use per-position winners)"
        }
        help_texts = {
            "numWinners": "At-large winner cap (leave blank/zero to use per-position winners)"
        }


class ElectionAdmin(admin.ModelAdmin):
    form = ElectionAdminForm


class PositionAdmin(admin.ModelAdmin):
    list_display = ("id", "election", "title", "winners", "enabled", "sort")
    list_editable = ("winners",)
    list_filter = ("election", "enabled")


@admin.register(RegionalPost)
class RegionalPostAdmin(admin.ModelAdmin):
    list_display = ("id", "region_slug", "title", "display_order", "created_at", "updated_at")
    list_filter = ("region_slug",)
    search_fields = ("title", "excerpt", "body")
    ordering = ("region_slug", "display_order", "-created_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(RegionalVideo)
class RegionalVideoAdmin(admin.ModelAdmin):
    list_display = ("id", "region_slug", "title", "video_type", "display_order", "created_at", "updated_at")
    list_filter = ("region_slug", "video_type")
    search_fields = ("title", "caption", "embed_url")
    ordering = ("region_slug", "display_order", "-created_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(RegionalOfficer)
class RegionalOfficerAdmin(admin.ModelAdmin):
    list_display = ("id", "region_slug", "group", "position", "name", "display_order", "updated_at")
    list_filter = ("region_slug", "group")
    search_fields = ("name", "position")
    ordering = ("region_slug", "group", "display_order", "name")
    readonly_fields = ("created_at", "updated_at")


# --- Standard model registrations ---

admin.site.register(User, UserAdmin)
admin.site.register(MembershipTypes)
admin.site.register(UserMembership, UserMembershipAdmin)
admin.site.register(Vote)
admin.site.register(Candidacy)
admin.site.register(Officer)
admin.site.register(Election, ElectionAdmin)
admin.site.register(Event)
admin.site.register(EventRating)
admin.site.register(EventRegistration, EventRegistrationAdmin)
admin.site.register(Venue)
admin.site.register(Attendance)
admin.site.register(Achievement)
admin.site.register(NewsandOffers)
admin.site.register(Position, PositionAdmin)


# --- Device push tokens + admin action ---

logger = logging.getLogger(__name__)


@admin.action(description="Send test push to selected tokens")
def send_test_push(modeladmin, request, queryset):
    """
    Admin action: send a small test push to the selected tokens.
    """
    client = PushClient()

    for device in queryset.filter(is_active=True):
        message = PushMessage(
            to=device.token,
            title="PAPSAS test notification",
            body="This is a test push from the admin.",
            data={"eventId": 3},  # demo event ID; adjust later if needed
        )
        try:
            client.publish(message)
        except DeviceNotRegisteredError:
            # Expo says token is no longer valid – mark it inactive
            DevicePushToken.objects.filter(pk=device.pk).update(is_active=False)
        except PushServerError as exc:
            logger.warning(
                "PushServerError for token %s (DevicePushToken %s): %s",
                device.token,
                device.pk,
                exc,
            )
        except Exception as exc:
            # Avoid breaking the admin action completely
            logger.warning(
                "Unexpected push error for token %s (DevicePushToken %s): %s",
                device.token,
                device.pk,
                exc,
            )


@admin.register(DevicePushToken)
class DevicePushTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "platform", "token_short", "is_active", "created_at")
    list_filter = ("platform", "is_active", "created_at")
    search_fields = ("user__username", "user__email", "token")
    actions = [send_test_push]

    @admin.display(description="Token")
    def token_short(self, obj: DevicePushToken) -> str:
        return f"{obj.token[:24]}..."
