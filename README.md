# FDA Recall Checker

A standalone web application to fetch, store, and view FDA medical device recalls. Originally designed as an ERPNext app, now converted to a standalone Flask application that can run on Ubuntu and be accessed from Windows machines.

## Features

- **Automatic FDA Data Fetching**: Fetches recalls from the FDA API daily
- **Web Interface**: Browse and search recalls through a modern web UI
- **REST API**: Access recall data programmatically via API endpoints
- **Statistics Dashboard**: View recall statistics and trends
- **Search Functionality**: Search recalls by device name, recall number, or firm
- **Scheduled Updates**: Automatic daily fetching at 2:00 AM

## Quick Start (Development)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize the database:**
   ```bash
   python3 -c "from app import app, init_db; init_db()"
   ```

3. **Run the development server:**
   ```bash
   python3 run.py
   ```

4. **Access the application:**
   - Open your browser to `http://localhost:5000`
   - Click "Fetch New Recalls" to import data from the FDA API

## Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions on deploying to an Ubuntu server with:
- Gunicorn (WSGI server)
- Nginx (reverse proxy)
- Supervisor (process management)
- Automatic daily fetching

## Project Structure

```
fda_recall_checker/
├── app.py                 # Main Flask application
├── models.py              # Database models (SQLAlchemy)
├── routes.py              # API routes and blueprints
├── database.py            # Database initialization
├── fetch_fda_recalls.py   # FDA API fetching logic
├── scheduler.py           # Background scheduler for daily fetches
├── wsgi.py                # Production WSGI entry point
├── run.py                 # Development server
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── recalls.html
│   ├── recall_detail.html
│   └── stats.html
└── static/                # Static files (CSS, JS)
    └── css/
        └── style.css
```

## API Endpoints

### Web Pages
- `GET /` - Dashboard
- `GET /recalls` - List all recalls (with pagination and search)
- `GET /recall/<id>` - View recall details
- `GET /stats` - Statistics page

### API Endpoints
- `GET /api/recalls` - Get recalls (JSON, with pagination)
- `GET /api/recalls/<id>` - Get specific recall (JSON)
- `GET /api/stats` - Get statistics (JSON)
- `POST /fetch` - Manually trigger recall fetch

### Query Parameters
- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 50)
- `search` - Search term (searches device name, recall number, firm)

## Database

The application uses SQLite by default (can be changed to PostgreSQL via `DATABASE_URL` environment variable).

Database location: `fda_recalls.db` (in the application directory)

## Environment Variables

- `DATABASE_URL` - Database connection string (default: `sqlite:///fda_recalls.db`)
- `SECRET_KEY` - Flask secret key for sessions (change in production!)
- `FLASK_ENV` - Flask environment (`development` or `production`)

## Future: ERPNext Integration

This application can be integrated with ERPNext to:
1. Compare FDA recalls against your inventory
2. Automatically flag items that match recalled devices
3. Generate alerts when new recalls affect your inventory

The REST API endpoints make it easy to integrate with ERPNext's API or create custom scripts.

## License

MIT License

## Author

SurgiShop - gary.starr@surgishop.com
