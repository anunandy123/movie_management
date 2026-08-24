from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from .models import Booking, Genre, Language, Movie, Review, Showtime, Theater


class MovieRulesTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(username='viewer', password='pass12345')
		self.language = Language.objects.create(name='English')
		self.genre = Genre.objects.create(name='Drama', slug='drama')
		self.movie = Movie.objects.create(
			title='Test Film', slug='test-film', description='A test film.',
			release_date='2026-01-01', language=self.language,
			trailer_url='https://www.youtube.com/watch?v=abc123',
		)
		self.movie.genres.add(self.genre)

	def test_trailer_is_embedded_with_privacy_enhanced_host(self):
		self.assertEqual(self.movie.trailer_embed_url, 'https://www.youtube-nocookie.com/embed/abc123')

	def test_non_youtube_trailer_is_rejected(self):
		self.movie.trailer_url = 'https://example.com/trailer'
		with self.assertRaises(ValidationError):
			self.movie.full_clean()

	def test_verified_viewer_requires_watched_booking(self):
		review = Review.objects.create(movie=self.movie, user=self.user, rating=5, title='Great', body='Loved it')
		self.assertFalse(review.is_verified_viewer)
		theater = Theater.objects.create(name='Main', city='London', address='1 High Street')
		showtime = Showtime.objects.create(movie=self.movie, theater=theater, starts_at=timezone.now() - timedelta(hours=2))
		Booking.objects.create(user=self.user, showtime=showtime, status='watched')
		self.assertTrue(review.is_verified_viewer)

	def test_movie_detail_renders_without_image_or_review_count_errors(self):
		response = self.client.get(self.movie.get_absolute_url())
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Test Film')
		self.assertContains(response, '0 reviews')

	def test_booking_rejects_malformed_seat_count(self):
		theater = Theater.objects.create(name='Main', city='London', address='1 High Street')
		showtime = Showtime.objects.create(movie=self.movie, theater=theater, starts_at=timezone.now() + timedelta(hours=2))
		self.client.force_login(self.user)
		response = self.client.post(f'/bookings/{showtime.pk}/', {'seats': 'many'})
		self.assertEqual(response.status_code, 302)
		self.assertFalse(Booking.objects.filter(user=self.user, showtime=showtime).exists())

	def test_review_rejects_rating_outside_range(self):
		theater = Theater.objects.create(name='Main', city='London', address='1 High Street')
		showtime = Showtime.objects.create(movie=self.movie, theater=theater, starts_at=timezone.now() - timedelta(hours=2))
		Booking.objects.create(user=self.user, showtime=showtime, status='watched')
		self.client.force_login(self.user)
		response = self.client.post(f'/movies/{self.movie.slug}/review/', {'rating': '6'})
		self.assertEqual(response.status_code, 302)
		self.assertFalse(Review.objects.filter(movie=self.movie, user=self.user).exists())
