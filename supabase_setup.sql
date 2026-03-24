-- ===================================
-- SUPABASE DATABASE SCHEMA SETUP
-- ===================================
-- Jalankan semua query ini di Supabase SQL Editor

-- 1. TABLE PREDICTIONS (Menyimpan history prediksi)
CREATE TABLE predictions (
    id BIGSERIAL PRIMARY KEY,
    student_name VARCHAR(255) NOT NULL,
    sleep_duration FLOAT NOT NULL,
    study_hours FLOAT NOT NULL,
    social_media_hours FLOAT NOT NULL,
    physical_activity FLOAT NOT NULL,
    prediction_result INT NOT NULL,
    stress_category VARCHAR(50) NOT NULL,
    deskripsi TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. TABLE MODEL_VERSIONS (Versi model untuk tracking)
CREATE TABLE model_versions (
    id BIGSERIAL PRIMARY KEY,
    model_name VARCHAR(255) NOT NULL,
    accuracy FLOAT NOT NULL,
    learning_rate FLOAT NOT NULL,
    iterations INT NOT NULL,
    total_correct_predictions INT NOT NULL,
    total_test_data INT NOT NULL,
    parameters JSONB,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. TABLE FEEDBACKS (Feedback akurasi dari user)
CREATE TABLE feedbacks (
    id BIGSERIAL PRIMARY KEY,
    prediction_id BIGINT REFERENCES predictions(id) ON DELETE CASCADE,
    user_feedback VARCHAR(50), -- 'correct', 'incorrect', 'neutral'
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. TABLE STUDENTS (Profil student untuk tracking)
CREATE TABLE students (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255),
    total_predictions INT DEFAULT 0,
    last_prediction_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. INDEX untuk performa query
CREATE INDEX idx_predictions_student_name ON predictions(student_name);
CREATE INDEX idx_predictions_created_at ON predictions(created_at);
CREATE INDEX idx_predictions_stress_category ON predictions(stress_category);
CREATE INDEX idx_students_name ON students(name);
CREATE INDEX idx_model_versions_is_active ON model_versions(is_active);

-- 6. Enable RLS (Row Level Security) - Optional untuk keamanan
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedbacks ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_versions ENABLE ROW LEVEL SECURITY;

-- 7. Create RLS Policies - Izinkan akses publik untuk sekarang
-- Policies untuk PREDICTIONS table
CREATE POLICY "Allow INSERT for predictions" ON predictions
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow SELECT for predictions" ON predictions
    FOR SELECT USING (true);

CREATE POLICY "Allow UPDATE for predictions" ON predictions
    FOR UPDATE USING (true) WITH CHECK (true);

-- Policies untuk STUDENTS table
CREATE POLICY "Allow INSERT for students" ON students
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow SELECT for students" ON students
    FOR SELECT USING (true);

CREATE POLICY "Allow UPDATE for students" ON students
    FOR UPDATE USING (true) WITH CHECK (true);

-- Policies untuk FEEDBACKS table
CREATE POLICY "Allow INSERT for feedbacks" ON feedbacks
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow SELECT for feedbacks" ON feedbacks
    FOR SELECT USING (true);

-- Policies untuk MODEL_VERSIONS table
CREATE POLICY "Allow INSERT for model_versions" ON model_versions
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow SELECT for model_versions" ON model_versions
    FOR SELECT USING (true);

CREATE POLICY "Allow UPDATE for model_versions" ON model_versions
    FOR UPDATE USING (true) WITH CHECK (true);
