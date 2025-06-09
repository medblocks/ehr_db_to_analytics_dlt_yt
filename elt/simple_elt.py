#!/usr/bin/env python3
import os
import dlt
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

def run_elt_pipeline():
    """ELT Pipeline using dlt - Extract, Load (replica), Transform (views)"""
    print("Starting ELT pipeline...")
    
    # Build connection strings
    source_postgres_url = f"postgresql://{get_env_var('SOURCE_POSTGRES_USER')}:{get_env_var('SOURCE_POSTGRES_PASSWORD')}@{get_env_var('SOURCE_POSTGRES_HOST')}:{get_env_var('SOURCE_POSTGRES_PORT')}/{get_env_var('SOURCE_POSTGRES_DATABASE')}"
    dest_postgres_url = f"postgresql://{get_env_var('POSTGRES_USER')}:{get_env_var('POSTGRES_PASSWORD')}@{get_env_var('POSTGRES_HOST')}:{get_env_var('POSTGRES_PORT')}/{get_env_var('POSTGRES_DATABASE')}"
    
    print(f"Connecting to Source PostgreSQL: {get_env_var('SOURCE_POSTGRES_HOST')}:{get_env_var('SOURCE_POSTGRES_PORT')}")
    print(f"Connecting to Destination PostgreSQL: {get_env_var('POSTGRES_HOST')}:{get_env_var('POSTGRES_PORT')}")
    
    # EXTRACT & LOAD: Create replica of source tables
    print("Step 1 & 2: Extract and Load - Creating replica of source data...")
    source = sql_database(source_postgres_url).with_resources("patients", "vitals")
    
    # Create pipeline
    pipeline = dlt.pipeline(
        pipeline_name="health_analytics",
        destination=dlt.destinations.postgres(dest_postgres_url),
        dataset_name="analytics"
    )
    
    # Load the raw data as replica (no transformation here)
    load_info = pipeline.run(source)
    print(f"Replica created successfully: {load_info}")
    
    # TRANSFORM: Create views for analytics (all transformation happens here)
    print("Step 3: Transform - Creating analytical views...")
    create_analytical_views(pipeline)
    
    print("ELT pipeline completed successfully")

def create_analytical_views(pipeline):
    """TRANSFORM step: Create simplified view for average pulse rate by age group"""
    print("Creating analytical view for average pulse rate by age group...")
    
    # Use the pipeline's SQL client directly
    with pipeline.sql_client() as client:
        
        # Create a single materialized view for pulse rate analytics by age group
        print("Creating materialized view for pulse rate by age group...")
        client.execute_sql("""
            DROP MATERIALIZED VIEW IF EXISTS mv_pulse_rate_by_age_group;
            CREATE MATERIALIZED VIEW mv_pulse_rate_by_age_group AS
            SELECT 
                CASE 
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.date_of_birth)) < 18 THEN '0-17'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.date_of_birth)) < 35 THEN '18-34'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.date_of_birth)) < 50 THEN '35-49'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.date_of_birth)) < 65 THEN '50-64'
                    ELSE '65+'
                END as age_group,
                COUNT(*) as total_readings,
                COUNT(DISTINCT p.patient_id) as unique_patients,
                ROUND(AVG(v.pulse_rate), 1) as avg_pulse_rate
            FROM analytics.patients p
            JOIN analytics.vitals v ON p.patient_id = v.patient_id
            GROUP BY 
                CASE 
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.date_of_birth)) < 18 THEN '0-17'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.date_of_birth)) < 35 THEN '18-34'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.date_of_birth)) < 50 THEN '35-49'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.date_of_birth)) < 65 THEN '50-64'
                    ELSE '65+'
                END
            ORDER BY 
                CASE 
                    CASE 
                        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.date_of_birth)) < 18 THEN '0-17'
                        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.date_of_birth)) < 35 THEN '18-34'
                        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.date_of_birth)) < 50 THEN '35-49'
                        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.date_of_birth)) < 65 THEN '50-64'
                        ELSE '65+'
                    END
                    WHEN '0-17' THEN 1 WHEN '18-34' THEN 2 WHEN '35-49' THEN 3 
                    WHEN '50-64' THEN 4 WHEN '65+' THEN 5
                END;
        """)
        
        # Create index for performance
        print("Creating index for performance...")
        client.execute_sql("""
            CREATE INDEX IF NOT EXISTS idx_pulse_rate_age_group ON mv_pulse_rate_by_age_group(age_group);
        """)
        
        print("Pulse rate analytics view created successfully!")

if __name__ == "__main__":
    try:
        run_elt_pipeline()
    except Exception as e:
        print(f"ELT Pipeline failed: {e}")
        raise 