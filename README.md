# Healthcare Analytics ETL with dlt

A simplified ETL pipeline using [dlt](https://dlthub.com) to analyze patient vitals by age group.

## Quick Start

### 1. Start the databases

```bash
docker-compose up -d
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create environment file

```bash
cp .env.example .env
```

Edit `.env` with your database credentials if different from the defaults.


### 4. Run the ETL pipeline

```bash
python etl/simple_etl.py
```

### 5. Start the API server

```bash
python api/simple_api.py
```

The API will be available at `http://localhost:5001` with endpoints:

- `/api/vitals-by-age-group` - Get aggregated vitals data
- `/api/refresh` - Refresh the materialized view

## What it does

1. **Extracts** patient and vitals data from MySQL using dlt's SQL source
2. **Transforms** data by creating joined tables with age groups using SQL
3. **Loads** raw data into PostgreSQL using dlt's destination
4. **Creates** a materialized view for instant analytics

## Key Features

- **Unified database operations** through dlt
- **Automatic schema management** with dlt
- **Built-in error handling** and retries
- **SQL-based transformations** using PostgreSQL
- **Generic configuration** - no hardcoded values

## Dependencies

```
dlt[duckdb,mysql,postgres,sql_database]>=0.3.5  # Main ETL framework
python-dotenv==1.0.1                            # Environment variables
flask==3.0.2                                    # API server
flask-cors==4.0.0                               # CORS support
pymysql>=1.0.0                                  # MySQL driver for dlt
psycopg2-binary>=2.9.0                          # PostgreSQL driver for dlt
cryptography>=3.4.0                             # Required for MySQL authentication
```

## Configuration

All database settings are in `.env`:

```env
# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=demouser
MYSQL_PASSWORD=demopassword
MYSQL_DATABASE=healthdata

# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=demouser
POSTGRES_PASSWORD=demopassword
POSTGRES_DATABASE=analytics
```

## Architecture

```
MySQL (Source) → dlt Pipeline → PostgreSQL (Destination)
     ↓              ↓                    ↓
  patients +    Load raw data    →   SQL transformations
   vitals    →  with dlt        →    + materialized view
```

## dlt Benefits

- **Declarative**: Define what you want, not how
- **Automatic**: Schema inference and creation
- **Reliable**: Built-in error handling and retries
- **Scalable**: Incremental loading support
- **Simple**: Minimal configuration required
- **Unified**: Single library handles all database operations
