from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Booking, Movie, Review, ReviewReport, Showtime


def home(request):
	movies = Movie.objects.prefetch_related('genres', 'images')
	return render(request, 'movies/home.html', {
		'featured_movies': movies.filter(featured=True)[:6],
		'trending_movies': movies.order_by('-view_count')[:6],
		'recent_movies': movies.order_by('-release_date')[:6],
	})


def signup(request):
	form = UserCreationForm(request.POST or None)
	if form.is_valid():
		user = form.save()
		login(request, user)
		return redirect('home')
	return render(request, 'registration/signup.html', {'form': form})


def movie_detail(request, slug):
	movie = get_object_or_404(Movie.objects.prefetch_related('genres', 'cast_members', 'images'), slug=slug)
	Movie.objects.filter(pk=movie.pk).update(view_count=movie.view_count + 1)
	similar = Movie.objects.filter(
		Q(genres__in=movie.genres.all()) | Q(language=movie.language)
	).exclude(pk=movie.pk).distinct()[:4]
	return render(request, 'movies/detail.html', {
		'movie': movie,
		'showtimes': movie.showtimes.filter(starts_at__gte=timezone.now()).select_related('theater'),
		'reviews': movie.reviews.filter(is_published=True).select_related('user'),
		'review_count': movie.reviews.filter(is_published=True).count(),
		'similar_movies': similar,
	})


@login_required
def book_showtime(request, showtime_id):
	showtime = get_object_or_404(Showtime, pk=showtime_id)
	if request.method == 'POST':
		try:
			seats = int(request.POST.get('seats', 1))
		except (TypeError, ValueError):
			seats = 0
		if seats < 1:
			messages.error(request, 'Choose at least one seat.')
		elif showtime.has_ended:
			messages.error(request, 'This screening has already ended.')
		else:
			with transaction.atomic():
				showtime = Showtime.objects.select_for_update().get(pk=showtime.pk)
				if seats <= showtime.seats_available:
					Booking.objects.create(user=request.user, showtime=showtime, seats=seats)
					showtime.seats_available -= seats
					showtime.save(update_fields=['seats_available'])
					messages.success(request, 'Your booking is confirmed.')
				else:
					messages.error(request, 'Not enough seats are available.')
	return redirect(showtime.movie.get_absolute_url())


@login_required
def submit_review(request, slug):
	movie = get_object_or_404(Movie, slug=slug)
	eligible = Booking.objects.filter(user=request.user, showtime__movie=movie, status='watched').exists()
	if not eligible:
		messages.error(request, 'Reviews are available after an administrator marks your booking as watched.')
		return redirect(movie.get_absolute_url())
	if request.method == 'POST':
		try:
			rating = int(request.POST.get('rating', 5))
		except (TypeError, ValueError):
			rating = 0
		if not 1 <= rating <= 5:
			messages.error(request, 'Rating must be between 1 and 5.')
		else:
			Review.objects.update_or_create(
				movie=movie, user=request.user,
				defaults={'rating': rating, 'title': request.POST.get('title', ''), 'body': request.POST.get('body', '')},
			)
			messages.success(request, 'Your review has been saved.')
	return redirect(movie.get_absolute_url())


@login_required
def report_review(request, review_id):
	review = get_object_or_404(Review, pk=review_id)
	if request.method == 'POST':
		ReviewReport.objects.get_or_create(review=review, reporter=request.user, defaults={'reason': request.POST.get('reason', 'Inappropriate content')})
		messages.success(request, 'Thanks. The review has been sent for moderation.')
	return redirect(review.movie.get_absolute_url())
