#!/usr/bin/env python3
import os
import dlt
from datetime import datetime
from dotenv import load_dotenv
from dlt.sources.sql_database import sql_database

# Load environment variables
load_dotenv()

def get_env_var(key, default=None):
    """Get environment variable with error handling"""
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Environment variable {key} is not set")
    return value

def calculate_age_group(date_of_birth):
    """Calculate age group from date of birth"""
    age = (datetime.now() - datetime.strptime(str(date_of_birth), '%Y-%m-%d')).days // 365
    if age < 18: return "0-17"
    elif age < 35: return "18-34"
    elif age < 50: return "35-49"
    elif age < 65: return "50-64"
    else: return "65+"

def run_etl_pipeline():
    """ETL Pipeline using dlt for Age Group Analysis"""
    print("Starting ETL pipeline...")
    
    # Build connection strings
    mysql_url = f"mysql+pymysql://{get_env_var('MYSQL_USER')}:{get_env_var('MYSQL_PASSWORD')}@{get_env_var('MYSQL_HOST')}:{get_env_var('MYSQL_PORT')}/{get_env_var('MYSQL_DATABASE')}"
    postgres_url = f"postgresql://{get_env_var('POSTGRES_USER')}:{get_env_var('POSTGRES_PASSWORD')}@{get_env_var('POSTGRES_HOST')}:{get_env_var('POSTGRES_PORT')}/{get_env_var('POSTGRES_DATABASE')}"
    
    print(f"Connecting to MySQL: {get_env_var('MYSQL_HOST')}:{get_env_var('MYSQL_PORT')}")
    print(f"Connecting to PostgreSQL: {get_env_var('POSTGRES_HOST')}:{get_env_var('POSTGRES_PORT')}")
    
    # First, load both tables to get the data
    source = sql_database(mysql_url).with_resources("patients", "vitals")
    
    # Create pipeline
    pipeline = dlt.pipeline(
        pipeline_name="health_analytics",
        destination=dlt.destinations.postgres(postgres_url),
        dataset_name="analytics"
    )
    
    # Load the raw data first
    print("Loading raw data...")
    load_info = pipeline.run(source)
    print(f"Raw data loaded: {load_info}")
    
    # Now create the joined and transformed data
    create_vitals_by_age_table(pipeline)
    
    # Create materialized view
    create_analytics_view(pipeline)
    print("ETL completed successfully")

def create_vitals_by_age_table(pipeline):
    """Create the vitals_by_age table with age groups using SQL"""
    print("Creating vitals_by_age table...")
    
    # Use the pipeline's SQL client directly
    with pipeline.sql_client() as client:
        # Create the joined table with age groups using SQL
        client.execute_sql("""
            DROP TABLE IF EXISTS vitals_by_age;
            CREATE TABLE vitals_by_age AS
            SELECT 
                p.patient_id,
                p.date_of_birth,
                v.temperature,
                v.pulse_rate,
                v.blood_pressure_systolic,
                v.blood_pressure_diastolic,
                CASE 
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.date_of_birth)) < 18 THEN '0-17'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.date_of_birth)) < 35 THEN '18-34'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.date_of_birth)) < 50 THEN '35-49'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.date_of_birth)) < 65 THEN '50-64'
                    ELSE '65+'
                END as age_group
            FROM patients p
            JOIN vitals v ON p.patient_id = v.patient_id;
        """)
        
        # Create index for performance
        client.execute_sql("""
            CREATE INDEX IF NOT EXISTS idx_vitals_age_group ON vitals_by_age(age_group);
        """)

def create_analytics_view(pipeline):
    """Create materialized view for analytics"""
    print("Creating materialized view...")
    
    # Use the pipeline's SQL client directly
    with pipeline.sql_client() as client:
        client.execute_sql("""
            DROP MATERIALIZED VIEW IF EXISTS mv_vitals_by_age_group;
            CREATE MATERIALIZED VIEW mv_vitals_by_age_group AS
            SELECT 
                age_group,
                COUNT(*) as total_readings,
                ROUND(AVG(temperature), 1) as avg_temperature,
                ROUND(AVG(pulse_rate), 0) as avg_pulse_rate,
                ROUND(AVG(blood_pressure_systolic), 0) as avg_systolic,
                ROUND(AVG(blood_pressure_diastolic), 0) as avg_diastolic
            FROM vitals_by_age
            GROUP BY age_group
            ORDER BY 
                CASE age_group 
                    WHEN '0-17' THEN 1 WHEN '18-34' THEN 2 WHEN '35-49' THEN 3 
                    WHEN '50-64' THEN 4 WHEN '65+' THEN 5
                END;
        """)
        
        client.execute_sql("""
            CREATE INDEX IF NOT EXISTS idx_mv_age_group ON mv_vitals_by_age_group(age_group);
        """)

if __name__ == "__main__":
    try:
        run_etl_pipeline()
    except Exception as e:
        print(f"ETL Pipeline failed: {e}")
        raise 