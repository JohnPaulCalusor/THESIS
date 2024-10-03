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
    path('vote', views.vote, name="vote"),
    path('about_us', views.about, name="about"),
    path('become_member', views.become_member, name="become_member"),
    path('news_offers', views.news_offers, name="news_offers"),
    path('profile/<int:id>', views.profile, name="profile"),
    path('attendance_form/', views.attendance_form, name='attendance_form'),
    path('email_not_verified/<int:user_id>/', views.email_not_verified, name='email_not_verified'),
    path('resend_verification_code/<int:user_id>/', views.resend_verification_code, name='resend_verification_code'),
    # election
    path('election', views.election, name="election"),
    path('election/manage/<int:id>', views.manage_election, name="manage_election"),
    # event
    path('event/calendar/', views.event_calendar, name='event_calendar'),
    path('event/<int:event_id>/register/', views.event_registration_view, name='event_registration_view'),
    path('event/list', views.event_list, name='event_list'),
    # membership
    path('membership_registration/<int:mem_id>', views.membership_registration, name="membership_registration"),
    path('membership_record/approve/<int:id>', views.approve_membership, name="approve_membership"),
    path('membership_record/decline/<int:id>', views.decline_membership, name="decline_membership"),
    path('membership-registration/delete/<int:id>', views.delete_membership, name="delete_membership"),
    # ganto nalang dapat url, - not _
    path('get-user-info/<int:id>/', views.get_user_info, name='get_user_info'),
    path('approve_membership/<int:id>', views.approve_membership, name="approve_membership"),
    # password
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('password_reset_verify/<int:user_id>/', views.password_reset_verify, name='password_reset_verify'),
    path('password_reset_confirm/<int:user_id>/', views.password_reset_confirm, name='password_reset_confirm'),
    # compose
    path('compose/event', views.event, name="event"),
    path('compose/venue', views.compose_venue, name="compose_venue"),
    path('compose/achievement', views.compose_achievement, name="compose_achievement"),
    path('compose/news_offer', views.compose_news_offer, name="compose_news_offer"),
    # record
    path('record/account', views.record, name="record"),
    path('record/attendance', views.attendance_list, name="attendance_list"),
    path('record/membership', views.membership_record, name="membership_record"),
    path('record/venue', views.venue_record, name="venue_record"),
    path('record/achievement', views.achievement_record, name="achievement_record"),
    path('record/news_offers', views.news_offers_record, name="news_offers_record"),
    # get function
    path('record/get-receipt/<int:user_id>/', views.get_receipt, name='get_receipt'),
    path('record/get-id/<int:user_id>/', views.get_id, name='get_id'),
    path('get-candidates/<int:election_id>/', views.get_officers, name="get_officers"),
    # get htmx
    path('record/get-attendance/<int:event_id>/', views.get_attendees, name='get_attendance'),
    path('partial/event', views.get_event, name="get_event"),
    path('partial/account', views.get_account, name="get_account"),
    #achievement
    path('achievement/', views.achievement_view, name='achievement'),
    #user
    path('user/delete/<int:id>', views.delete_account, name="delete_account"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)