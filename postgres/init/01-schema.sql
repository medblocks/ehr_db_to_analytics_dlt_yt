-- Initialize simplified schema for health data for PostgreSQL

-- Function to update modified_at column
CREATE OR REPLACE FUNCTION update_modified_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create patients table
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(36) NOT NULL UNIQUE,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    gender VARCHAR(50),
    date_of_birth DATE NOT NULL,
    ethnicity VARCHAR(50),
    race VARCHAR(50),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    insurance_provider VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_patient_id_patients ON patients(patient_id);
CREATE INDEX idx_name_patients ON patients(last_name, first_name);
CREATE INDEX idx_modified_at_patients ON patients(modified_at);

CREATE TRIGGER update_patients_modtime
    BEFORE UPDATE ON patients
    FOR EACH ROW
    EXECUTE PROCEDURE update_modified_at_column();

-- Create vitals table
CREATE TABLE vitals (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(36) NOT NULL,
    recorded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    temperature DECIMAL(5,2),
    pulse_rate INT,
    respiratory_rate INT,
    blood_pressure_systolic INT,
    blood_pressure_diastolic INT,
    oxygen_saturation DECIMAL(5,2),
    height DECIMAL(5,2),
    weight DECIMAL(5,2),
    bmi DECIMAL(5,2),
    pain_scale INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);

CREATE INDEX idx_patient_id_vitals ON vitals(patient_id);
CREATE INDEX idx_recorded_at_vitals ON vitals(recorded_at);
CREATE INDEX idx_modified_at_vitals ON vitals(modified_at);

CREATE TRIGGER update_vitals_modtime
    BEFORE UPDATE ON vitals
    FOR EACH ROW
    EXECUTE PROCEDURE update_modified_at_column(); 