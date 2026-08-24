from django.contrib import admin

from .models import Booking, CastMember, Genre, Language, Movie, MovieImage, Review, ReviewReport, Showtime, Theater


class MovieImageInline(admin.TabularInline):
	model = MovieImage
	extra = 1


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
	list_display = ('title', 'release_date', 'language', 'age_certification', 'featured', 'view_count')
	list_filter = ('featured', 'age_certification', 'language', 'genres')
	search_fields = ('title', 'description', 'tagline')
	prepopulated_fields = {'slug': ('title',)}
	filter_horizontal = ('genres', 'cast_members')
	inlines = [MovieImageInline]


@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
	list_display = ('movie', 'theater', 'starts_at', 'screen', 'seats_available', 'price')
	list_filter = ('theater', 'starts_at')
	date_hierarchy = 'starts_at'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
	list_display = ('movie', 'user', 'rating', 'is_published', 'created_at')
	list_filter = ('is_published', 'rating')
	search_fields = ('movie__title', 'user__username', 'title', 'body')


@admin.register(ReviewReport)
class ReviewReportAdmin(admin.ModelAdmin):
	list_display = ('review', 'reporter', 'is_resolved', 'created_at')
	list_filter = ('is_resolved',)


for model in (Genre, Language, CastMember, Theater, Booking):
	admin.site.register(model)
