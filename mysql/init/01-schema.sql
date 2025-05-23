-- Initialize simplified schema for health data

-- Create patients table
CREATE TABLE patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
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
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_patient_id (patient_id),
    INDEX idx_name (last_name, first_name),
    INDEX idx_modified_at (modified_at)
);

-- Create vitals table
CREATE TABLE vitals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(36) NOT NULL,
    recorded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
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
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    INDEX idx_patient_id (patient_id),
    INDEX idx_recorded_at (recorded_at),
    INDEX idx_modified_at (modified_at)
); 