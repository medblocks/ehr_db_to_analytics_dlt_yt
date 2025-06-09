-- Populate sample data for PostgreSQL

-- Insert sample patients (50 patients)
DO $$
DECLARE
    i INT := 1;
    genders TEXT[] := ARRAY['Male', 'Female', 'Non-binary'];
    ethnicities TEXT[] := ARRAY['Hispanic or Latino', 'Not Hispanic or Latino', 'Unknown'];
    races TEXT[] := ARRAY['White', 'Black or African American', 'Asian', 'American Indian or Alaska Native', 'Native Hawaiian or Other Pacific Islander'];
    cities TEXT[] := ARRAY['Anytown', 'Springfield', 'Metropolis', 'Gotham', 'Star City'];
    states TEXT[] := ARRAY['CA', 'NY', 'TX', 'FL', 'IL'];
BEGIN
    FOR i IN 1..50 LOOP
        INSERT INTO patients (
            patient_id, last_name, first_name, gender, date_of_birth,
            ethnicity, race, city, state, zip_code, insurance_provider
        )
        VALUES (
            'P' || LPAD(i::TEXT, 6, '0'),
            'LastName' || i,
            'FirstName' || i,
            genders[floor(random() * 3) + 1],
            CURRENT_DATE - (floor(random() * 30000) * interval '1 day'),
            ethnicities[floor(random() * 3) + 1],
            races[floor(random() * 5) + 1],
            cities[floor(random() * 5) + 1],
            states[floor(random() * 5) + 1],
            LPAD((floor(random() * 90000) + 10000)::TEXT, 5, '0'),
            'InsuranceCo ' || chr(65 + floor(random() * 5)::INT)
        );
    END LOOP;
END;
$$;

-- Insert sample vitals (3-8 vitals per patient)
DO $$
DECLARE
    patient_rec RECORD;
    vitals_count INT;
BEGIN
    FOR patient_rec IN SELECT patient_id FROM patients LOOP
        vitals_count := floor(random() * 6) + 3; -- 3-8 vitals per patient
        FOR j IN 1..vitals_count LOOP
            INSERT INTO vitals (
                patient_id, recorded_at, temperature, pulse_rate, respiratory_rate,
                blood_pressure_systolic, blood_pressure_diastolic, oxygen_saturation,
                height, weight, bmi, pain_scale
            )
            VALUES (
                patient_rec.patient_id,
                NOW() - (floor(random() * 365) * interval '1 day'),
                ROUND((36.0 + (random() * 2.5))::numeric, 1), -- Temp in Celsius (36-38.5)
                floor(60 + random() * 40)::INT, -- Pulse 60-100
                floor(12 + random() * 8)::INT, -- Resp rate 12-20
                floor(100 + random() * 40)::INT, -- Systolic 100-140
                floor(60 + random() * 30)::INT, -- Diastolic 60-90
                ROUND((95 + (random() * 5))::numeric, 1), -- O2 Sat 95-100
                ROUND((150 + (random() * 40))::numeric, 1), -- Height in cm
                ROUND((50 + (random() * 50))::numeric, 1), -- Weight in kg
                ROUND((18.5 + (random() * 16.5))::numeric, 1), -- BMI 18.5-35
                floor(random() * 11)::INT -- Pain 0-10
            );
        END LOOP;
    END LOOP;
END;
$$; 