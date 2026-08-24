from urllib.parse import parse_qs, urlparse

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Avg
from django.urls import reverse
from django.utils import timezone


class Genre(models.Model):
	name = models.CharField(max_length=80, unique=True)
	slug = models.SlugField(unique=True)

	class Meta:
		ordering = ['name']

	def __str__(self):
		return self.name


class Language(models.Model):
	name = models.CharField(max_length=80, unique=True)

	class Meta:
		ordering = ['name']

	def __str__(self):
		return self.name


class CastMember(models.Model):
	name = models.CharField(max_length=160)
	role = models.CharField(max_length=120, blank=True)
	photo = models.ImageField(upload_to='cast/', blank=True)

	class Meta:
		ordering = ['name']

	def __str__(self):
		return self.name


class Movie(models.Model):
	CERTIFICATIONS = [('U', 'U'), ('PG', 'PG'), ('12A', '12A'), ('15', '15'), ('18', '18')]
	title = models.CharField(max_length=200)
	slug = models.SlugField(unique=True)
	tagline = models.CharField(max_length=240, blank=True)
	description = models.TextField()
	release_date = models.DateField()
	duration_minutes = models.PositiveIntegerField(default=120)
	age_certification = models.CharField(max_length=4, choices=CERTIFICATIONS, default='12A')
	language = models.ForeignKey(Language, on_delete=models.PROTECT, related_name='movies')
	genres = models.ManyToManyField(Genre, related_name='movies')
	cast_members = models.ManyToManyField(CastMember, blank=True, related_name='movies')
	trailer_url = models.URLField(blank=True, help_text='YouTube watch, shorts, or youtu.be URL only.')
	featured = models.BooleanField(default=False)
	view_count = models.PositiveIntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-release_date', 'title']

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('movie-detail', kwargs={'slug': self.slug})

	@property
	def average_rating(self):
		return self.reviews.filter(is_published=True).aggregate(value=Avg('rating'))['value'] or 0

	@property
	def trailer_embed_url(self):
		if not self.trailer_url:
			return ''
		parsed = urlparse(self.trailer_url)
		if parsed.netloc in {'youtu.be', 'www.youtu.be'}:
			video_id = parsed.path.strip('/').split('/')[0]
		elif parsed.netloc.endswith('youtube.com'):
			video_id = parse_qs(parsed.query).get('v', [''])[0]
			if parsed.path.startswith('/shorts/'):
				video_id = parsed.path.split('/')[2]
		else:
			return ''
		return f'https://www.youtube-nocookie.com/embed/{video_id}' if video_id else ''

	def clean(self):
		if self.trailer_url and not self.trailer_embed_url:
			raise ValidationError({'trailer_url': 'Use a valid YouTube URL.'})



class MovieImage(models.Model):
	movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='images')
	image = models.ImageField(upload_to='posters/')
	caption = models.CharField(max_length=120, blank=True)
	is_primary = models.BooleanField(default=False)
	sort_order = models.PositiveIntegerField(default=0)

	class Meta:
		ordering = ['sort_order', 'id']

	def __str__(self):

		return f'{self.movie.title} poster'


class Theater(models.Model):
	name = models.CharField(max_length=160)
	city = models.CharField(max_length=100)
	address = models.TextField()


	class Meta:
		ordering = ['city', 'name']

	def __str__(self):
		return f'{self.name}, {self.city}'


class Showtime(models.Model):
	movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='showtimes')
	theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name='showtimes')
	starts_at = models.DateTimeField()
	screen = models.CharField(max_length=40, default='Screen 1')
	seats_total = models.PositiveIntegerField(default=80)
	seats_available = models.PositiveIntegerField(default=80)
	price = models.DecimalField(max_digits=7, decimal_places=2, default=12.00)

	class Meta:
		ordering = ['starts_at']


	def __str__(self):
		return f'{self.movie} at {self.starts_at:%d %b, %H:%M}'

	@property
	def has_ended(self):
		return self.starts_at < timezone.now()


class Booking(models.Model):
	STATUS_CHOICES = [('reserved', 'Reserved'), ('watched', 'Watched'), ('cancelled', 'Cancelled')]
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
	showtime = models.ForeignKey(Showtime, on_delete=models.PROTECT, related_name='bookings')

	seats = models.PositiveIntegerField(default=1)
	status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='reserved')
	booked_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-booked_at']

	def __str__(self):
		return f'{self.user} - {self.showtime}'


class Review(models.Model):
	movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
	rating = models.PositiveSmallIntegerField()
	title = models.CharField(max_length=160)
	body = models.TextField()
	is_published = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at']
		constraints = [models.UniqueConstraint(fields=['movie', 'user'], name='one_review_per_user_movie')]


	def __str__(self):
		return f'{self.movie} review by {self.user}'

	@property
	def is_verified_viewer(self):
		return Booking.objects.filter(user=self.user, showtime__movie=self.movie, status='watched').exists()

	def clean(self):
		if not 1 <= self.rating <= 5:
			raise ValidationError({'rating': 'Rating must be between 1 and 5.'})


class ReviewReport(models.Model):
	review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='reports')
	reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	reason = models.TextField()
	is_resolved = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f'Report on review #{self.review_id}'
