# 🎬 Videoflix - Video Streaming Platform

Videoflix is a fully functional video streaming platform (inspired by Netflix) that allows users to create accounts, log in securely, and stream videos with adaptive bitrate quality (HLS).

The project consists of a **Django Backend** (DRF) handling the API, authentication, and video processing, and a **Frontend** delivering the user interface.

## ✨ Features

### 👤 User Management & Authentication
* **Registration:** Users can sign up using their email address and password.
* **Email Activation:** Accounts must be verified via a secure activation link sent by email.
* **Secure Login:** implementation using **JWT** (JSON Web Tokens) stored in HttpOnly cookies for maximum security.
* **Password Reset:** "Forgot Password" flow allowing users to reset credentials via email.

### 🎥 Video Streaming & Processing
* **Video Upload:** Admins can upload video files directly via the Django Admin Panel.
* **Automated Transcoding:** Background workers (Redis & Django-RQ) automatically convert uploaded videos into **480p, 720p, and 1080p** resolutions.
* **HLS Streaming:** Content is served as `.m3u8` playlists for smooth, adaptive streaming across different bandwidths.
* **Content API:** Endpoints to fetch video lists, details, and metadata.

---

## 🛠 Tech Stack

### Backend
* **Framework:** Django & Django Rest Framework (DRF)
* **Database:** PostgreSQL
* **Async Tasks:** Django-RQ & Redis (for video conversion & emails)
* **Video Processing:** FFmpeg
* **Authentication:** JWT (SimpleJWT) with Cookie storage

### Frontend
* **Core:** HTML5, CSS3, JavaScript (Vanilla)
* **Video Player:** Custom HLS integration

### DevOps
* **Containerization:** Docker & Docker Compose
* **Server:** Gunicorn / Nginx (ready for deployment)

---

## 🚀 Installation & Setup

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running.
* Git

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR-USERNAME/videoflix-backend.git](https://github.com/YOUR-USERNAME/videoflix-backend.git)
cd videoflix-backend
```

2. Environment Configuration (.env)
Create a .env file in the root directory (same level as docker-compose.yml) and add your configuration:

# --- Django Settings ---
```bash
SECRET_KEY=your-super-secret-key-change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

# --- Database (PostgreSQL) ---
```bash
DB_NAME=videoflix_db
DB_USER=videoflix_user
DB_PASSWORD=supersecretpassword
DB_HOST=db
DB_PORT=5432
```

# --- Redis (Task Queue) ---
```bash
REDIS_LOCATION=redis://redis:6379/1
```

# --- Email Settings (SMTP) ---
# For development, you can use the console backend (prints to terminal)
# For production, use a real SMTP server (e.g., Gmail)
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=Videoflix <no-reply@videoflix.com>
```

# --- Frontend Connection ---
# Used to generate correct links in emails
FRONTEND_URL=http://localhost:5500


3. Start with Docker
Launch the entire stack (Database, Backend, Redis, Worker) with a single command:
```bash
docker-compose up --build
```

Note: The first launch might take a few minutes as Docker images are being built.


4. Database Migration & Admin User
Open a new terminal window (while Docker is running) and execute:

# 1. Apply database migrations
```bash
docker-compose exec web python manage.py migrate
```
# 2. Create an admin user (to upload videos)
```bash
docker-compose exec web python manage.py createsuperuser
```

🎮 Usage Guide
Admin Panel (Uploads)
URL: http://localhost:8000/admin/

Log in with your superuser account.

Navigate to Videos and upload a new file.

Watch the magic: The background worker will pick up the file and start converting it. You can see the progress in your Docker terminal logs.

Frontend (Streaming)
URL: http://localhost:5500 (assuming you serve it via Live Server or similar).

Register a new user.

Check your console (or email) for the Activation Link.

Log in and click on a video to start streaming!

🧪 Testing
To run the automated test suite for the backend:


docker-compose exec web python manage.py test


📄 License
This project was created for educational purposes.