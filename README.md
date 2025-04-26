# FleetSecure

A Django-based application for managing fleet drivers and trucks.

## Features

- **User Authentication**: JWT-based authentication with token blacklisting
- **Driver Management**: Create, update, and track drivers
- **Truck Management**: Assign trucks to drivers, track vehicle information
- **AWS S3 Integration**: Store profile pictures and documents in S3
- **Redis Integration**: For JWT token storage and caching
- **Security Features**: Rate limiting, secure headers, permission-based access control

## Technical Stack

- **Back end**: Django + Django REST Framework
- **Database**: PostgreSQL
- **Cache**: Redis
- **Storage**: AWS S3 (or LocalStack S3 for development)
- **Authentication**: JWT with token refresh
- **Docker**: Containerized deployment

## API Endpoints

### Authentication

- `POST /api/v1/auth/login/`: Login with username/password
- `POST /api/v1/auth/refresh/`: Refresh JWT token
- `POST /api/v1/auth/logout/`: Blacklist JWT token
- `POST /api/v1/auth/verify/`: Verify JWT token

### Users

- `GET /api/v1/users/`: List all users (admin only)
- `POST /api/v1/users/`: Create new user
- `GET /api/v1/users/{id}/`: Get user details
- `PATCH /api/v1/users/{id}/`: Update user
- `DELETE /api/v1/users/{id}/`: Delete user
- `GET /api/v1/users/me/`: Get current user profile
- `POST /api/v1/users/{id}/change_password/`: Change password
- `PATCH /api/v1/users/{id}/activate/`: Activate user (admin)
- `PATCH /api/v1/users/{id}/deactivate/`: Deactivate user (admin)

### Drivers

- `GET /api/v1/drivers/`: List all drivers
- `POST /api/v1/drivers/`: Create new driver
- `GET /api/v1/drivers/{id}/`: Get driver details
- `PATCH /api/v1/drivers/{id}/`: Update driver
- `DELETE /api/v1/drivers/{id}/`: Delete driver
- `GET /api/v1/drivers/me/`: Get current user's driver profile
- `PATCH /api/v1/drivers/{id}/activate/`: Activate driver
- `PATCH /api/v1/drivers/{id}/deactivate/`: Deactivate driver

### Trucks

- `GET /api/v1/trucks/`: List all trucks
- `POST /api/v1/trucks/`: Create new truck
- `GET /api/v1/trucks/{id}/`: Get truck details
- `PATCH /api/v1/trucks/{id}/`: Update truck
- `DELETE /api/v1/trucks/{id}/`: Delete truck
- `GET /api/v1/trucks/by_driver/?driver_id=X`: Filter trucks by driver
- `GET /api/v1/trucks/by_year/?year=X`: Filter trucks by year

## Development Setup

### Requirements

- Docker
- Docker Compose

### Getting Started

1. Clone the repository
2. Create `.env` file (use `.env.example` as template)
3. Run `docker-compose up --build`
4. Access the API at `http://localhost:8000/api/v1/`

### Environment Variables

Required environment variables are documented in `.env.example`.
