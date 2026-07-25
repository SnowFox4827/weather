# Flask Weather Dashboard

This is a Flask-based weather dashboard application that fetches weather data from the OpenWeatherMap API and displays it in a user-friendly interface.

## Configuration

Use a `.env` file to store sensitive information and environment-specific settings. **Do not commit `.env` to version control.**

### .env Example

```
API_KEY=your_api_key_here
```
Use a `config.json` file to store location information. **Do not commit `config.json` to version control.**

### config.json Example

```
  "city": "",
  "state": "",
  "country": ""
```

## Dependencies

The project uses the following packages (see `requirements.txt`):

- **Flask**: Web framework for routes, templates, and the dashboard.
- **requests**: For making HTTP calls to the OpenWeatherMap API.
- **python-dotenv**: Loads environment variables from `.env`.

### requirements.txt

```
Flask
requests
python-dotenv
```

## Docker Setup

### Dockerfile

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["python", "app.py"]
```

### docker-compose
```docker-compose.yml
services:
  weather-app:
    build: .
    container_name: weather-app

    ports:
      - "5001:5001"

    env_file:
      - .env

    volumes:
      - ./config.json:/app/config.json

    restart: unless-stopped
```

This will:
- Ensure the environment and volumes are set
- Make it where the container doesn't stop if there's an error

### Building and Running

1. Ensure you have Docker and Docker Compose installed.
2. Place your `.env` file in the project root.
3. Run the following command:

```bash
docker compose up -d --build
```

This will:
- Build the Python image.
- Install dependencies.
- Copy application files.
- Load `.env` via Docker Compose.
- Start the Flask app on port 5001.

Access the dashboard at: [http://localhost:5001](http://localhost:5001)

## .gitignore Recommendation

```
.env
```

## Additional Notes

- Keep API keys and secrets out of source code using `.env`.
- Each developer or deployment can have different settings without code changes.
