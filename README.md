# Groktor-X

Grok-powered intelligent search system for X (formerly Twitter) posts. This application enables semantic search, AI-enhanced query understanding, and intelligent summarization of social media content.

## Table of Contents

- [Features](#features)
- [Technical Specifications](#technical-specifications)
- [Architecture](#architecture)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Database Population](#database-population)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)

## Features

### AI-Enhanced Search

- Grok-powered query understanding and semantic matching
- Automatic query enhancement with intent extraction and keyword expansion
- Intelligent result summarization using Grok API
- Natural language query processing

### Advanced Search Capabilities

- Token-based search engine with boolean operator support (AND, OR, NOT)
- Relevance scoring based on keyword matches and engagement metrics
- Multiple sort options: relevance, date, likes, retweets
- Author filtering and content type filtering

### Data Management

- Comprehensive post metadata storage (engagement metrics, hashtags, mentions, media, links)
- Automatic content type detection (text, text_link, text_media, media_only, link_only)
- AI-generated post descriptions for enhanced searchability
- Duplicate prevention during data population

### User Interface

- Google-like search interface with dynamic layout
- Real-time search with loading states
- Filter tabs for author, content type, and sorting
- Responsive design matching X's aesthetic
- Expandable result summaries

## Technical Specifications

### Backend Stack

- **Framework**: FastAPI 0.115.0+
- **Language**: Python 3.13
- **ORM**: SQLAlchemy 2.0.36+
- **Database**: SQLite (with pysqlite driver)
- **HTTP Client**: httpx 0.27.0+ (async)
- **API Integration**: Grok API (x.ai)
- **Server**: Uvicorn with standard extensions

### Frontend Stack

- **Framework**: React 18.2.0
- **Language**: TypeScript 5.2.2
- **Build Tool**: Vite 5.0.8
- **Styling**: TailwindCSS 3.4.0
- **HTTP Client**: Native Fetch API

### Database Schema

- **Post Model**: Comprehensive metadata including:
  - Core identifiers (id, author, author_display_name)
  - Content (content, timestamp, post_url, post_type, content_type)
  - Engagement metrics (likes, retweets, replies, quotes, bookmarks, views)
  - Content metadata (hashtags, mentions, media_urls, link_urls)
  - AI metadata (grok_description, is_processed)
  - System metadata (created_at, updated_at)

### Search Engine

- Token-based indexing with boolean operator parsing
- Relevance scoring algorithm considering:
  - Keyword match frequency
  - Engagement metrics (likes, retweets)
  - Content type relevance
  - Timestamp recency
- Support for complex queries: `AI AND space`, `technology OR innovation`, `AI NOT crypto`

## Architecture

### Backend Architecture

**Application Layer** (`app/main.py`)

- FastAPI application initialization
- CORS middleware configuration
- Database initialization on startup
- Route registration

**API Layer** (`app/api/routes.py`)

- RESTful API endpoints
- Request/response validation with Pydantic
- Database session management
- Error handling

**Service Layer**

- **GrokClient** (`app/services/grok_client.py`): Grok API integration
  - Query enhancement (intent extraction, keyword expansion)
  - Post description generation
  - Result summarization
- **SearchService** (`app/services/search_service.py`): Search engine
  - Query tokenization and parsing
  - Boolean operator processing
  - Relevance scoring
  - Result sorting

**Data Layer**

- **Database Models** (`app/models/database.py`): SQLAlchemy ORM models
- **Database Utilities** (`app/utils/db_utils.py`): CRUD operations, content type detection

**Configuration** (`app/config.py`)

- Environment variable management with Pydantic Settings
- Database URL configuration
- API key management

### Frontend Architecture

**Component Structure**

- **App.tsx**: Main application component with search logic and state management
- **SearchResults.tsx**: Search results display and summary rendering
- **PostCard.tsx**: Individual post display component
- **Summary.tsx**: Grok-generated summary with expandable view
- **Filters.tsx**: Filter UI component (author, content type, sort)

**Service Layer** (`src/services/api.ts`)

- API client for backend communication
- Type-safe request/response handling

**Type System** (`src/types/index.ts`)

- TypeScript interfaces for API contracts
- Type safety for search requests and responses

### Data Flow

1. User enters search query in frontend
2. Frontend sends POST request to `/api/search` with query and filters
3. Backend enhances query using Grok API (intent, keywords, expanded terms)
4. SearchService performs token-based search with boolean operators
5. Results are scored and sorted based on relevance and filters
6. Grok API generates summary of top results
7. Enhanced query data and summary returned to frontend
8. Frontend displays results with filters and summary

## Deployment

### Prerequisites

- Docker and Docker Compose installed
- Grok API Key from x.ai

### Docker Deployment (Recommended)

#### Step 1: Environment Setup

Create a `.env` file in the project root:

```env
GROK_API_KEY=your_api_key_here
GROK_API_URL=https://api.x.ai/v1
```

#### Step 2: Build and Start Containers

```bash
docker-compose up --build
```

This command will:

- Build the backend container (Python 3.13, FastAPI, all dependencies)
- Build the frontend container (Node.js build, nginx serving)
- Start both services with proper networking

#### Step 3: Populate Database

In a new terminal, populate the database with sample tweets:

```bash
docker-compose exec backend python scripts/populate_sample_data.py --count 50
```

This generates 50 unique AI-generated tweets using Grok API. The process takes approximately 2-5 minutes (2 API calls per tweet: one for generation, one for description).

#### Step 4: Access Application

- Frontend: http://localhost
- Backend API: http://localhost:8000

### Docker Commands Reference

**Start services:**

```bash
docker-compose up --build
```

**Start in background (detached mode):**

```bash
docker-compose up -d
```

**Stop services:**

```bash
docker-compose down
```

**View logs:**

```bash
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Rebuild after code changes:**

```bash
docker-compose up --build
```

**Check container status:**

```bash
docker-compose ps
```

**Execute commands in container:**

```bash
docker-compose exec backend bash
docker-compose exec backend python scripts/populate_sample_data.py --count 50
```

**Stop and remove everything (including volumes):**

```bash
docker-compose down -v
```

### Docker Configuration

**Backend Container** (`backend/Dockerfile`)

- Base image: Python 3.13-slim
- Installs system dependencies (gcc for Python packages)
- Copies requirements and installs Python dependencies
- Sets working directory and environment variables
- Exposes port 8000
- Runs uvicorn server

**Frontend Container** (`frontend/Dockerfile`)

- Multi-stage build:
  - Build stage: Node.js 20-alpine, installs dependencies, builds React app
  - Production stage: nginx-alpine, serves static files
- Nginx configuration includes API proxy to backend
- Exposes port 80

**Docker Compose** (`docker-compose.yml`)

- Defines backend and frontend services
- Configures networking between containers
- Sets up volume mounts for database persistence
- Loads environment variables from `.env` file
- Configures restart policies

### Local Development (Without Docker)

#### Backend Setup

```bash
cd backend
python -m venv ../venv
source ../venv/bin/activate  # On Windows: ..\venv\Scripts\activate
pip install -r requirements.txt
```

#### Frontend Setup

```bash
cd frontend
npm install
```

#### Environment Configuration

Create `.env` file in project root:

```env
GROK_API_KEY=your_api_key_here
GROK_API_URL=https://api.x.ai/v1
DATABASE_URL=sqlite+pysqlite:///./posts.db
```

#### Running Locally

**Backend:**

```bash
cd backend
python scripts/run_api.py
# Or: uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm run dev
```

## API Documentation

### Search Endpoint

**POST /api/search**

Search posts with Grok-enhanced query understanding.

**Request Body:**

```json
{
  "query": "AI AND space",
  "limit": 20,
  "offset": 0,
  "author": "elonmusk",
  "content_type": "text",
  "sort_by": "relevance",
  "use_grok_enhancement": true,
  "include_summary": true
}
```

**Parameters:**

- `query` (required): Search query string. Supports boolean operators (AND, OR, NOT)
- `limit` (optional, default: 20): Maximum number of results (1-100)
- `offset` (optional, default: 0): Pagination offset
- `author` (optional): Filter by author username
- `content_type` (optional): Filter by content type (text, text_link, text_media, media_only, link_only)
- `sort_by` (optional, default: "relevance"): Sort option (relevance, date, likes, retweets)
- `use_grok_enhancement` (optional, default: true): Enable Grok query enhancement
- `include_summary` (optional, default: true): Include Grok-generated summary

**Response:**

```json
{
  "results": [
    {
      "id": "1234567890",
      "author": "elonmusk",
      "author_display_name": "Elon Musk",
      "content": "AI will fundamentally change...",
      "timestamp": "2024-01-15T10:30:00",
      "likes": 50000,
      "retweets": 10000,
      "replies": 5000,
      "quotes": 2000,
      "bookmarks": 5000,
      "views": 1000000,
      "post_url": "https://x.com/elonmusk/status/1234567890",
      "post_type": "tweet",
      "content_type": "text",
      "hashtags": ["AI", "Future"],
      "mentions": [],
      "media_urls": [],
      "link_urls": [],
      "grok_description": "Post about AI and future technology..."
    }
  ],
  "total": 96,
  "limit": 20,
  "offset": 0,
  "query": "AI AND space",
  "enhanced_query": {
    "intent": "Searching for posts about AI and space exploration",
    "keywords": ["AI", "space", "exploration"],
    "expanded_terms": ["artificial intelligence", "space technology"],
    "query_type": "general"
  },
  "summary": "The search results show discussions about AI applications in space exploration..."
}
```

**Example Usage:**

```bash
# Basic search
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "AI", "limit": 10}'

# Search with filters
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "technology OR innovation",
    "author": "elonmusk",
    "sort_by": "likes",
    "limit": 20
  }'

# Boolean operators
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "AI AND space NOT crypto", "limit": 15}'
```

### Get Post Endpoint

**GET /api/posts/{post_id}**

Retrieve a specific post by ID.

**Response:**

```json
{
  "id": "1234567890",
  "author": "elonmusk",
  "content": "...",
  "timestamp": "2024-01-15T10:30:00",
  ...
}
```

### List Posts Endpoint

**GET /api/posts**

List posts with optional filtering.

**Query Parameters:**

- `limit` (optional, default: 20): Number of results (1-100)
- `offset` (optional, default: 0): Pagination offset
- `author` (optional): Filter by author username

**Example:**

```bash
curl "http://localhost:8000/api/posts?limit=10&author=elonmusk"
```

### Rate Limit Considerations

**Grok API Rate Limits:**

- The Grok API has rate limits that vary by plan
- Each search request makes 1-2 API calls (query enhancement + optional summary)
- Each post generation makes 2 API calls (tweet generation + description)
- Implement exponential backoff for production use
- Consider caching query enhancements for repeated searches

**Recommendations:**

- Cache Grok query enhancements for common queries
- Batch post description generation when possible
- Monitor API usage and implement rate limiting on your side
- Use `use_grok_enhancement: false` for testing to reduce API calls

**Error Handling:**

- The application gracefully handles Grok API failures
- If query enhancement fails, falls back to original query
- If summary generation fails, results are returned without summary
- Check logs for API error details

## Database Population

### Using Docker

**Populate with sample tweets:**

```bash
docker-compose exec backend python scripts/populate_sample_data.py --count 50
```

**View database contents:**

```bash
docker-compose exec backend python scripts/view_descriptions.py --limit 10
docker-compose exec backend python scripts/view_descriptions.py --author elonmusk --limit 20
```

**Clean up database:**

```bash
docker-compose exec backend python scripts/cleanup_db.py --clean-all
docker-compose exec backend python scripts/cleanup_db.py --clean-authors elonmusk sama
docker-compose exec backend python scripts/cleanup_db.py --stats
```

### Using Local Environment

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Populate database
cd backend
python scripts/populate_sample_data.py --count 50

# View descriptions
python scripts/view_descriptions.py --limit 10

# Clean up
python scripts/cleanup_db.py --clean-all
```

### Population Script Details

**populate_sample_data.py**

Generates unique AI-generated tweets using Grok API.

**Features:**

- Generates tweets for configured accounts (elonmusk, sama, realDonaldTrump)
- Uses Grok API to generate unique tweet content based on topics
- Ensures no duplicate content (checks in-memory set and database)
- Automatically generates Grok descriptions for searchability
- Retry logic if duplicates are detected (up to 3 attempts per tweet)

**Usage:**

```bash
python scripts/populate_sample_data.py --count 50
```

**Options:**

- `--count N`: Number of tweets to generate (default: 50)

**Process:**

1. Selects random account and topic
2. Calls Grok API to generate tweet content
3. Checks for duplicates (in-memory and database)
4. Generates Grok description for the tweet
5. Creates post in database with metadata
6. Repeats until count is reached

**Time Estimate:**

- Approximately 2-5 minutes for 50 tweets
- 2 API calls per tweet (generation + description)
- ~2-3 seconds per API call

## Troubleshooting

### Docker Issues

**Docker daemon not running:**

```
Error: Cannot connect to the Docker daemon
```

Solution: Start Docker Desktop and wait for it to fully initialize before running docker-compose commands.

**Port conflicts:**

```
Error: bind: address already in use
```

Solution: Change ports in `docker-compose.yml` or stop the service using the port:

```bash
# Find process using port 8000
lsof -i :8000
# Kill the process or change port in docker-compose.yml
```

**Container build failures:**

```
Error: failed to solve
```

Solution:

- Check internet connection
- Verify Docker has enough resources allocated
- Try rebuilding without cache: `docker-compose build --no-cache`

**Database not persisting:**
Solution: Verify volume mounts in `docker-compose.yml`. Database should be in `./backend/data/posts.db`.

### API Issues

**Grok API errors:**

```
Grok API HTTP error: 401
```

Solution:

- Verify `GROK_API_KEY` is set correctly in `.env` file
- Check API key is valid and not expired
- Ensure `.env` file is in project root

**Grok API rate limits:**

```
Grok API HTTP error: 429
```

Solution:

- Reduce number of concurrent requests
- Implement delays between API calls
- Check your Grok API plan limits
- Cache query enhancements

**Database connection errors:**

```
sqlite3.OperationalError: no such table: posts
```

Solution: Database not initialized. Run:

```bash
docker-compose exec backend python -c "from app.models.database import init_db; init_db()"
```

### Frontend Issues

**Frontend can't reach backend:**
Solution:

- Verify both containers are running: `docker-compose ps`
- Check nginx proxy configuration in frontend Dockerfile
- Verify API URL in frontend environment variables
- Check browser console for CORS errors

**Build failures:**

```
npm ERR! code ELIFECYCLE
```

Solution:

- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check Node.js version (requires 20+)
- Verify package.json is valid

### Search Issues

**No results returned:**

- Verify database is populated: `docker-compose exec backend python scripts/view_descriptions.py --limit 1`
- Check search query syntax (boolean operators are case-sensitive: AND, OR, NOT)
- Verify filters aren't too restrictive

**Slow search performance:**

- Database may be large; consider adding indexes
- Grok API calls add latency; disable `use_grok_enhancement` for testing
- Check database file size and optimize if needed

### General Debugging

**View container logs:**

```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Check container status:**

```bash
docker-compose ps
docker ps
```

**Access container shell:**

```bash
docker-compose exec backend bash
docker-compose exec frontend sh
```

**Verify environment variables:**

```bash
docker-compose exec backend env | grep GROK
```

**Test database:**

```bash
docker-compose exec backend python -c "from app.models.database import SessionLocal, Post; db = SessionLocal(); print(f'Posts: {db.query(Post).count()}'); db.close()"
```

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py          # API endpoints
│   │   ├── models/
│   │   │   └── database.py        # SQLAlchemy models
│   │   ├── services/
│   │   │   ├── grok_client.py     # Grok API integration
│   │   │   └── search_service.py  # Search engine
│   │   ├── utils/
│   │   │   └── db_utils.py        # Database utilities
│   │   ├── config.py              # Configuration
│   │   └── main.py                # FastAPI application
│   ├── scripts/
│   │   ├── populate_sample_data.py
│   │   ├── view_descriptions.py
│   │   ├── cleanup_db.py
│   │   └── run_api.py
│   ├── tests/                     # Test suite
│   ├── data/                      # Database storage (Docker)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/            # React components
│   │   ├── services/              # API client
│   │   ├── types/                 # TypeScript types
│   │   └── App.tsx
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

## License

MIT
