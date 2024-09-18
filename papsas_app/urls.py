# import path
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name="index"),
    path('register/' , views.register, name="register"),
    path('logout', views.logout_view, name="logout"),
    path('login', views.login_view, name="login"),
    path('verify_email/<int:user_id>/', views.verify_email, name='verify_email'),
    path('election', views.election, name="election"),
    path('manageElection/<int:id>', views.manage_election, name="manage_election"),
    path('vote', views.vote, name="vote"),
    path('profile/<int:id>', views.profile, name="profile"),
    path('attendance_form/', views.attendance_form, name='attendance_form'),
    # event
    path('event/calendar/', views.event_calendar, name='event_calendar'),
    path('event/<int:event_id>/register/', views.event_registration_view, name='event_registration_view'),
    path('event/list', views.event_list, name='event_list'),
    path('about_us', views.about, name="about"),
    path('become_member', views.become_member, name="become_member"),
    path('news_offers', views.news_offers, name="news_offers"),
    path('record', views.record, name="record"),
    # membership
    path('membership_registration/<int:mem_id>', views.membership_registration, name="membership_registration"),
    path('membership_record', views.membership_record, name="membership_record"),
    path('membership_record/approve_membership/<int:id>', views.approve_membership, name="approve_membership"),
    path('membership_record/decline_membership/<int:id>', views.decline_membership, name="decline_membership"),
    # ganto nalang dapat url, - not _
    path('get-user-info/<int:id>/', views.get_user_info, name='get_user_info'),
    path('approve_membership/<int:id>', views.approve_membership, name="approve_membership"),
    # password
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('password_reset_verify/<int:user_id>/', views.password_reset_verify, name='password_reset_verify'),
    path('password_reset_confirm/<int:user_id>/', views.password_reset_confirm, name='password_reset_confirm'),
    # compose
    path('compose/event', views.event, name="event"),
    path('compose/venue', views.compose_venue, name="compose_venue")
    path('email_not_verified/<int:user_id>/', views.email_not_verified, name='email_not_verified'),
    path('resend_verification_code/<int:user_id>/', views.resend_verification_code, name='resend_verification_code'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)