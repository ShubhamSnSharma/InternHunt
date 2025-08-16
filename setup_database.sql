-- InternHunt Database Setup Script
CREATE DATABASE IF NOT EXISTS internhunt;
USE internhunt;

-- Create users table for storing user information
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    skills TEXT,
    resume_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create jobs table for storing job postings
CREATE TABLE IF NOT EXISTS jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    description TEXT,
    requirements TEXT,
    salary_range VARCHAR(100),
    job_type VARCHAR(50),
    posted_date DATE,
    source VARCHAR(100),
    url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create applications table for tracking job applications
CREATE TABLE IF NOT EXISTS applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    job_id INT,
    status ENUM('applied', 'interview', 'rejected', 'accepted') DEFAULT 'applied',
    applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- Create courses table for storing course recommendations
CREATE TABLE IF NOT EXISTS courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    provider VARCHAR(255),
    category VARCHAR(100),
    difficulty_level ENUM('beginner', 'intermediate', 'advanced'),
    duration VARCHAR(50),
    description TEXT,
    url VARCHAR(500),
    rating DECIMAL(3,2),
    price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Show tables to confirm creation
SHOW TABLES;
