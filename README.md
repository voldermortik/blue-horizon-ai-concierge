# Blue Horizon AI Concierge

An intelligent AI concierge system for luxury hotels, powered by LlamaIndex and OpenAI.

## Features

- Natural language room booking and availability checks
- Personalized customer service with context awareness
- Real-time room availability management
- Integration with Neon PostgreSQL and Redis Cloud
- Vector search for hotel information and FAQs
- Dynamic pricing and occupancy management

## Project Structure

```
blue_horizon/
├── app/            # Main application code
│   ├── api.py     # FastAPI backend
│   └── streamlit_app.py  # Streamlit frontend
├── data/          # Data generation and management
│   ├── generators/  # Synthetic data generators
│   └── schemas/    # Data schemas and models
├── services/      # Core business logic
│   ├── nl2sql_service.py    # Natural language to SQL
│   ├── search_service.py    # Vector search
│   └── chat_service.py      # Chat handling
├── tools/         # Utility tools and helpers
├── tests/         # Test suite
└── utils/         # Utility functions
```

## Setup and Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/blue-horizon-ai-concierge.git
   cd blue-horizon-ai-concierge
   ```

2. **Install Poetry**
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install Dependencies**
   ```bash
   poetry install
   ```

4. **Set Up Environment Variables**
   - Copy `.env.example` to `.env`
   - Fill in your API keys and configuration

5. **Initialize Database**
   ```bash
   poetry run python scripts/init_neon_db.py
   ```

## Local Development

1. **Start the FastAPI Backend**
   ```bash
   poetry run python -m uvicorn app.api:app --reload --loop asyncio
   ```

2. **Start the Streamlit Frontend**
   ```bash
   poetry run streamlit run blue_horizon/app/streamlit_app.py
   ```

## Testing

```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_specific.py

# Run with coverage
poetry run pytest --cov=blue_horizon
```

## Deployment

### Streamlit Cloud Deployment

1. **Prerequisites**
   - A GitHub repository with your code
   - Accounts for:
     - [Streamlit Cloud](https://share.streamlit.io)
     - [Neon.tech](https://neon.tech) (PostgreSQL database)
     - [Redis Cloud](https://redis.com/cloud/overview/)
     - [OpenAI](https://platform.openai.com)

2. **Local Development**
   - The project uses Poetry for dependency management:
     ```bash
     # Install dependencies
     poetry install
     
     # Activate virtual environment
     poetry shell
     
     # Add new dependencies
     poetry add package_name
     ```

3. **Preparing for Deployment**
   - Generate `requirements.txt` for Streamlit Cloud:
     ```bash
     poetry export -f requirements.txt --output requirements.txt --without-hashes
     ```
   - Key dependencies are:
     - Database: `asyncpg`, `sqlalchemy`, `psycopg2-binary`
     - AI/ML: `openai`, `llama-index`, `sentence-transformers`
     - Frontend: `streamlit`
     - Caching: `redis`

4. **Environment Setup**
   - In Streamlit Cloud dashboard, add the following secrets:
     ```toml
     [openai]
     api_key = "your-actual-openai-key"

     [neon]
     db_url = "postgresql://user:password@your-db-host.cloud.neon.tech/dbname?sslmode=require"

     [redis]
     host = "your-redis-host.cloud.redislabs.com"
     port = "your-redis-port"
     password = "your-redis-password"
     ssl = "true"
     ssl_cert_reqs = "none"

     [app]
     environment = "production"
     log_level = "INFO"

     [security]
     jwt_secret_key = "your-jwt-secret"
     jwt_algorithm = "HS256"
     access_token_expire_minutes = "30"
     ```

5. **Deployment Process**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Select the main file path (e.g., `blue_horizon/app/streamlit_app.py`)
   - Set Python version to 3.12
   - Deploy!

6. **Continuous Development**
   - Make changes locally and test
   - Commit and push to GitHub
   - Streamlit Cloud will automatically redeploy
   - Monitor deployment status in Streamlit Cloud dashboard

7. **Best Practices**
   - Keep sensitive data in Streamlit Cloud secrets
   - Use `st.secrets` to access configuration
   - Test locally before pushing changes
   - Monitor application logs in Streamlit Cloud dashboard
   - Keep `requirements.txt` updated when adding new dependencies

### Local Development vs Cloud
- Local: Uses `.env` file for environment variables
- Cloud: Uses Streamlit secrets
- Both: Share the same codebase and configuration structure

For more details on specific configurations and troubleshooting, refer to the [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-cloud).

## Development Workflow

### Adding New Features

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Update Database (if needed)**
   - Add models in `blue_horizon/data/schemas/`
   - Create migrations in `scripts/`
   - Update data generators if needed

3. **Implement Features**
   - Add new services in `blue_horizon/services/`
   - Update API endpoints in `app/api.py`
   - Add frontend components in `app/streamlit_app.py`

4. **Testing**
   - Add unit tests in `tests/`
   - Test locally with both frontend and backend
   - Verify database migrations

5. **Documentation**
   - Update docstrings and comments
   - Update README if needed
   - Document any new environment variables

### Code Style and Standards

- Follow PEP 8 guidelines
- Use type hints
- Document functions and classes
- Keep functions focused and modular
- Use meaningful variable names

### Troubleshooting

1. **Database Connection Issues**
   - Verify Neon.tech connection string
   - Check SSL requirements
   - Verify network connectivity

2. **Redis Connection Issues**
   - Confirm Redis Cloud credentials
   - Check SSL settings
   - Verify connection timeout settings

3. **OpenAI API Issues**
   - Verify API key
   - Check rate limits
   - Monitor usage and quotas

4. **Streamlit Cloud Deployment Issues**
   - Check deployment logs
   - Verify secrets configuration
   - Confirm Python version compatibility
   - Check requirements.txt completeness

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

[License information here]
