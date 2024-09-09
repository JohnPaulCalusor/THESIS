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
    path('event', views.event, name="event"),
    path('attendance_form/', views.attendance_form, name='attendance_form'),
    path('event/<int:event_id>/register/', views.event_registration_view, name='event_registration_view'),
    path('about_us', views.about, name="about"),
    path('become_member', views.become_member, name="become_member"),
    path('news_offers', views.news_offers, name="news_offers"),
    path('record', views.record, name="record"),
    path('membership_registration/<int:mem_id>', views.membership_registration, name="membership_registration"),
    path('membership_record', views.membership_record, name="membership_record"),
    path('approve_membership/<int:id>', views.approve_membership, name="approve_membership"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)