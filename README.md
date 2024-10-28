# Library Management System

**Project Description**: This project is a library management web application that allows users to register, subscribe, browse books, and manage subscriptions. It also includes email notifications and supports authentication using JWT tokens.

## Technologies Used

- **Programming Language**: Python
- **Framework**: Django
- **Database**: PostgreSQL
- **Frontend**: Bootstrap 5, Django Templates
- **Payment Gateway**: Stripe
- **Task Queue**: Celery + Redis
- **Authentication**: JWT (using `rest_framework_simplejwt`)
- **Third-party Libraries**:
  - `django-taggit` - for tagging books
  - `crispy_forms` and `crispy_bootstrap5` - for enhanced form styling

## Installation and Setup

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis
- pip (Python package manager)

### Setup Steps

1. **Clone the repository:**

    ```bash
    git clone https://github.com/khachikmiroian/library-site.git
    cd library-site
    ```

2. **Create a virtual environment and install dependencies:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3. **Configure the database:**

   - Create a PostgreSQL database.
   - Create a `.env` file in the root directory of the project and add the following environment variables:

    ```env
    SECRET_KEY=your_secret_key_here
    NAME=your_database_name
    USER=your_database_user
    PASSWORD=your_database_password
    HOST=localhost
    PORT=5432
    EMAIL_HOST_USER=your_email@gmail.com
    EMAIL_HOST_PASSWORD=your_email_password
    STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
    STRIPE_SECRET_KEY=your_stripe_secret_key
    STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
    ```

4. **Apply the database migrations:**

    ```bash
    python manage.py migrate
    ```

5. **Create a superuser:**

    ```bash
    python manage.py createsuperuser
    ```

6. **Run the development server:**

    ```bash
    python manage.py runserver
    ```

7. **Run Celery:**

    Celery, which uses Redis as a broker, can be run using:

    ```bash
    celery -A librarysite worker --loglevel=info
    celery -A librarysite beat --loglevel=info
    ```

## Features

- **User Registration and Authentication**: Users can register, log in, and manage their profiles.
- **Subscription Management**: Users can manage their subscriptions using Stripe.
- **Library Management**: Admin users can add, edit, and delete books.
- **Book Tagging**: Tags are supported using `django-taggit`.
- **JWT Authentication**: The application uses JWT tokens for secure API authentication.
- **Background Tasks**: Uses Celery for executing background tasks (e.g., sending email notifications).

## Project Structure

- **accounts**: Handles user registration, authentication, and profile management.
- **books**: Module for managing books.
- **subscriptions**: Handles user subscriptions.
- **librarysite**: Main module containing project settings and configurations.

## Usage

- **Admin Panel**: Access the admin interface at `/admin/`, where administrators can manage users, books, and subscriptions.
- **API Endpoints**: REST API endpoints are available for interacting with the system, and they require JWT authentication.

## Environment Variables

The project requires several environment variables to run correctly. These are stored in a `.env` file:

- `SECRET_KEY` - Your Django secret key.
- `NAME`, `USER`, `PASSWORD`, `HOST`, `PORT` - PostgreSQL database configuration.
- `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` - Credentials for email service.
- `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` - Stripe API keys.

## Running Tests

To run the tests, use the following command:

```bash
python manage.py test
