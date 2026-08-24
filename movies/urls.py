from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('movies/<slug:slug>/', views.movie_detail, name='movie-detail'),
    path('movies/<slug:slug>/review/', views.submit_review, name='submit-review'),
    path('reviews/<int:review_id>/report/', views.report_review, name='report-review'),
    path('bookings/<int:showtime_id>/', views.book_showtime, name='book-showtime'),
]
