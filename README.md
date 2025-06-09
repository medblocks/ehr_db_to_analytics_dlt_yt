# Healthcare Analytics elt with dlt

A simplified elt pipeline using [dlt](https://dlthub.com) to replicate and transform data between PostgreSQL databases.

## Quick Start

### 1. Start the databases

This will start two PostgreSQL containers:

- `postgres_source`: A read-replica on port `5433` with sample data.
- `postgres_analytics`: A destination database on port `5432`.

```bash
docker-compose up -d
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create environment file

Create a `.env` file and add the following configuration. This file is ignored by git.

```env
# Source PostgreSQL Database (Read Replica)
SOURCE_POSTGRES_HOST=localhost
SOURCE_POSTGRES_PORT=5433
SOURCE_POSTGRES_USER=demouser
SOURCE_POSTGRES_PASSWORD=demopassword
SOURCE_POSTGRES_DATABASE=healthdata

# Destination PostgreSQL Database (Analytics)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=demouser
POSTGRES_PASSWORD=demopassword
POSTGRES_DATABASE=analytics
```

### 5. Run the elt pipeline

```bash
python elt/simple_elt.py
```

### 6. Start the API server

```bash
python api/simple_api.py
```

The API will be available at `http://localhost:5001` with endpoints:

- `/` - A simple HTML dashboard to view the data.
- `/api/vitals-by-age-group` - Get aggregated vitals data.
- `/api/refresh` - Refresh the materialized view with the latest data.


### 7. Redash

```bash
cd redash-setup
./setup-macos.sh
```

gets redash up and running on http://localhost:5005, the dockercompose is specifically set up for macos

## What it does

1.  **Extracts** patient and vitals data from a source PostgreSQL database using dlt's `sql_database` source.
2.  **Loads** raw data into a destination PostgreSQL database.
3.  **Transforms** the data by creating a new table (`vitals_by_age`) with calculated age groups.
4.  **Creates** a materialized view (`mv_vitals_by_age_group`) for fast, pre-aggregated analytics.

## Key Features

- **Declarative elt**: Define data sources and destinations without complex scripting.
- **Automatic Schema Management**: `dlt` automatically infers and adapts to the source schema.
- **PostgreSQL-based Transformations**: All data transformations are performed using SQL within the destination database.
- **Decoupled Architecture**: The source database, analytics database, and API are all independent services.

## Dependencies

```
dlt[postgres]>=0.3.5   # Main elt framework
python-dotenv==1.0.1                     # Environment variables
flask==3.0.2                             # API server
flask-cors==4.0.0                        # CORS support
psycopg2-binary>=2.9.0                   # PostgreSQL driver for dlt
cryptography>=3.4.0                      # Required for auth
```

## Configuration

All database settings are managed in the `.env` file. The application uses two PostgreSQL databases:

- **Source (`healthdata`)**: A read-replica of the production database.
- **Destination (`analytics`)**: A separate database for elt and analytics workloads.

## Architecture

```
PostgreSQL (Source) → dlt Pipeline → PostgreSQL (Destination)
      ↓                     ↓                    ↓
  patients table +     Load raw data    →   SQL transformations
   vitals table      →  with dlt        →    + materialized view
```

## dlt Benefits

- **Declarative**: Define what you want, not how.
- **Automatic**: Schema inference and evolution is handled automatically.
- **Reliable**: Includes built-in error handling, retries, and state management.
- **Scalable**: Supports incremental loading and scales to large datasets.
- **Simple**: Requires minimal configuration to get started.
- **Unified**: A single library can handle connections and operations for many sources and destinations.
