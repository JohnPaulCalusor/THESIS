# import path
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    get_total_members_count,
    get_total_events_count,
    get_total_revenue,
    get_membership_growth,
    get_avg_registration_vs_attendance,
)

urlpatterns = [
    path('', views.index, name="index"),
    path('register/', views.register, name="register"),
    path('logout', views.logout_view, name="logout"),
    path('login', views.login_view, name="login"),
    path('verify_email/<int:user_id>/', views.verify_email, name='verify_email'),
    path('vote', views.vote, name="vote"),
    path('about_us', views.about, name="about"),
    path('become_member', views.become_member, name="become_member"),
    path('news_offers', views.news_offers, name="news_offers"),
    path('profile/<int:id>', views.profile, name="profile"),
    path('profile/<int:id>/tor', views.upload_tor, name="upload_tor"),
    path('event/<int:event_id>/attendance_form/', views.attendance_form, name='attendance_form'),
    path('email_not_verified/<int:user_id>/', views.email_not_verified, name='email_not_verified'),
    path('resend_verification_code/<int:user_id>/', views.resend_verification_code, name='resend_verification_code'),
    # election
    path('election', views.election, name="election"),
    path('election/<int:id>/declare-candidacy', views.declare_candidacy, name="declare_candidacy"),
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
    path('record/membership', views.membership_record, name="membership_record"),
    path('record/venue', views.venue_record, name="venue_record"),
    path('record/achievement', views.achievement_record, name="achievement_record"),
    path('record/news_offers', views.news_offers_record, name="news_offers_record"),
    path('record/event-registration/decline/<int:id>', views.decline_eventReg, name="decline_eventReg"),
    path('record/event-registration/approve/<int:id>', views.approve_eventReg, name="approve_eventReg"),
    path('record/event-registration/delete/<int:id>', views.delete_eventReg, name="delete_eventReg"),
    # get function
    path('record/get-receipt/<int:user_id>/', views.get_receipt, name='get_receipt'),
    path('record/get-id/<int:user_id>/', views.get_id, name='get_id'),
    path('get-candidates/<int:election_id>/', views.get_officers, name="get_officers"),
    path('record/event/<int:id>/registration/', views.get_event_reg, name="get_event_reg"),
    path('get-achievement-data/<int:achievement_id>/', views.get_achievement_data, name='get_achievement_data'),
    # get htmx
    path('record/get-attendance/<int:event_id>/', views.get_attendees, name='get_attendance'),
    path('partial/event/<str:view>', views.get_event, name="get_event"),
    path('partial/profile/<int:id>', views.get_profile, name="get_profile"),
    # achievement
    path('achievement/', views.achievement_view, name='achievement'),
    path('achievement/delete/<int:id>/', views.delete_achievement, name="delete_achievement"),
    # user
    path('user/delete/<int:id>', views.delete_account, name="delete_account"),
    path('user/update/<int:id>', views.update_account, name="update_account"),
    #news and offers
    path('news_offers/delete/<int:id>', views.delete_news_offer, name='delete_news_offer'),
    path('news_offers/update/<int:id>/', views.update_news_offer, name='update_news_offer'),
    #venue
    path('venue/delete/<int:id>', views.delete_venue, name='delete_venue'),
    path('venue/update/<int:id>/', views.update_venue, name='update_venue'),
    #event
    path('event/delete/<int:id>', views.delete_event, name='delete_event'),
    path('event/update/<int:id>/', views.update_event, name='update_event'),
    # admin dashboard
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('get_membership_data/', views.get_membership_distribution_data, name='get_membership_data'),
    path('get_attendance_over_time_data/', views.get_attendance_over_time_data, name='get_attendance_over_time_data'),
    path('get_total_members_count/', get_total_members_count, name='get_total_members_count'),
    path('get_total_events_count/', get_total_events_count, name='get_total_events_count'),
    path('get_total_revenue/', get_total_revenue, name='get_total_revenue'),
    path('get_membership_growth/', get_membership_growth, name='get_membership_growth'),
    path('get_avg_registration_vs_attendance/', get_avg_registration_vs_attendance, name='get_avg_registration_vs_attendance'),    
    path('get_event_rating/', views.get_event_rating, name='get_event_rating'),
    path('get_user_distribution_by_region/', views.get_user_distribution_by_region, name='get_user_distribution_by_region'),
    path('get_event/<int:event_id>/rating/', views.box_plot, name='get_event_rating' ),
    path('events/boxplot/', views.box_event, name="box_event"),
    path('get_event_price_vs_attendance_data/', views.get_event_price_vs_attendance_data, name='get_event_price_vs_attendance_data'),

    # table
    path('table/user/', views.UserListView.as_view(), name='user_table'),
    path('table/membership/', views.MembershipListView.as_view(), name="membership_table"),
    path('table/user/membership/', views.UserMembershipListView.as_view(), name="user_membership_table"),
    path('table/event/', views.EventListView.as_view(), name="event_table"),
    path('table/venue/', views.VenueListView.as_view(), name="venue_table"),
    path('table/news-offers/', views.NewsAndOffersListView.as_view(), name="news_offers_table"),
    path('table/achievement/', views.AchievementListView.as_view(), name="achievement_table"),
    path('table/event-registration-table/<int:event_id>/', views.EventRegistrationListView.as_view(), name='event_registration_table'),
    path('table/election-table/<int:election_id>/', views.ElectionListView.as_view(), name='election_table'),
    path('table/user/event-registration-table/', views.UserEventRegistrationListView.as_view(), name='user_event_registration_table'),
    path('event-attendance-table/<int:event_id>/', views.EventAttendanceListView.as_view(), name='event_attendance_table'),
    path('table/user/event-attendance-table/', views.UserEventAttendanceListView.as_view(), name='user_event_attendance_table'),
    #generate qr/event rating
    path('event/<int:event_id>/generate-qr/', views.generate_qr, name='generate_qr'),
    path('event/<int:event_id>/rate/', views.rate_event, name='rate_event'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
