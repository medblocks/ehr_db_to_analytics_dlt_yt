-- Populate sample data

-- Insert sample patients (50 patients)
DELIMITER //
CREATE PROCEDURE InsertSamplePatients()
BEGIN
    DECLARE i INT DEFAULT 1;
    
    WHILE i <= 50 DO
        INSERT INTO patients (
            patient_id, last_name, first_name, gender, date_of_birth,
            ethnicity, race, city, state, zip_code, insurance_provider
        )
        VALUES (
            CONCAT('P', LPAD(i, 6, '0')),
            CONCAT('LastName', i),
            CONCAT('FirstName', i),
            ELT(FLOOR(RAND() * 3) + 1, 'Male', 'Female', 'Non-binary'),
            DATE_SUB(CURDATE(), INTERVAL FLOOR(RAND() * 30000) DAY),
            ELT(FLOOR(RAND() * 3) + 1, 'Hispanic or Latino', 'Not Hispanic or Latino', 'Unknown'),
            ELT(FLOOR(RAND() * 5) + 1, 'White', 'Black or African American', 'Asian', 'American Indian or Alaska Native', 'Native Hawaiian or Other Pacific Islander'),
            ELT(FLOOR(RAND() * 5) + 1, 'Anytown', 'Springfield', 'Metropolis', 'Gotham', 'Star City'),
            ELT(FLOOR(RAND() * 5) + 1, 'CA', 'NY', 'TX', 'FL', 'IL'),
            LPAD(FLOOR(RAND() * 90000) + 10000, 5, '0'),
            CONCAT('InsuranceCo ', CHAR(FLOOR(RAND() * 5) + 65)) -- A, B, C, D, E
        );
        SET i = i + 1;
    END WHILE;
END //
DELIMITER ;

CALL InsertSamplePatients();
DROP PROCEDURE InsertSamplePatients;

-- Insert sample vitals (3-8 vitals per patient)
DELIMITER //
CREATE PROCEDURE InsertSampleVitals()
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE patient_count INT;
    DECLARE patient_id_var VARCHAR(36);
    DECLARE vitals_count INT;
    DECLARE j INT;
    
    SELECT COUNT(*) INTO patient_count FROM patients;
    
    WHILE i <= patient_count DO
        SELECT patient_id INTO patient_id_var FROM patients WHERE id = i;
        SET vitals_count = FLOOR(RAND() * 6) + 3; -- 3-8 vitals per patient
        SET j = 1;
        
        WHILE j <= vitals_count DO
            INSERT INTO vitals (
                patient_id, recorded_at, temperature, pulse_rate, respiratory_rate,
                blood_pressure_systolic, blood_pressure_diastolic, oxygen_saturation,
                height, weight, bmi, pain_scale
            )
            VALUES (
                patient_id_var,
                DATE_SUB(NOW(), INTERVAL FLOOR(RAND() * 365) DAY),
                ROUND(36.0 + (RAND() * 2.5), 1), -- Temp in Celsius (36-38.5)
                FLOOR(60 + RAND() * 40), -- Pulse 60-100
                FLOOR(12 + RAND() * 8), -- Resp rate 12-20
                FLOOR(100 + RAND() * 40), -- Systolic 100-140
                FLOOR(60 + RAND() * 30), -- Diastolic 60-90
                ROUND(95 + (RAND() * 5), 1), -- O2 Sat 95-100
                ROUND(150 + (RAND() * 40), 1), -- Height in cm
                ROUND(50 + (RAND() * 50), 1), -- Weight in kg
                ROUND(18.5 + (RAND() * 16.5), 1), -- BMI 18.5-35
                FLOOR(RAND() * 11) -- Pain 0-10
            );
            SET j = j + 1;
        END WHILE;
        
        SET i = i + 1;
    END WHILE;
END //
DELIMITER ;

CALL InsertSampleVitals();
DROP PROCEDURE InsertSampleVitals; 