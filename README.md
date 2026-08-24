

# 🎬 Movie Management System

A Django-based web application to manage movies, genres, cast members, theaters, showtimes, and reviews. Designed as a full-stack project to demonstrate database modeling, admin customization, and deployment readiness.

---

## 🚀 Features
- **Authentication & Authorization**
  - User login, registration, and admin dashboard
  - Role-based access (superuser, staff, normal users)

- **Movie Management**
  - Add, edit, and delete movies
  - Associate movies with genres, languages, and cast members
  - Upload posters and metadata

- **Cast & Crew**
  - Maintain cast member profiles (actors, directors, etc.)
  - Link cast members to movies

- **Theaters & Showtimes**
  - Manage theaters and schedules
  - Bookings linked to users and showtimes

- **Reviews & Ratings**
  - Users can submit reviews and ratings
  - Admin moderation of review reports

---

## 🛠️ Tech Stack
- **Backend:** Django (Python 3.12+)
- **Database:** SQLite (default), easily switchable to PostgreSQL/MySQL
- **Frontend:** Django templates + Bootstrap
- **Environment:** Virtualenv / venv

---

## 📂 Project Structure
```
movie_management/
├── manage.py
├── movie_manage/        # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── movies/              # Main app
    ├── models.py
    ├── views.py
    ├── admin.py
    ├── templates/
    └── static/
```

---

## ⚙️ Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/anunandy123/movie_management.git
   cd movie_management
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/Mac
   .venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

7. **Access admin panel**
   - URL: `http://127.0.0.1:8000/admin/`
   - Login with your superuser credentials

