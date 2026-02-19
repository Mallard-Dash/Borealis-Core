--This is the database for Healthlogger 2.0. It is using Mariadb as RDBMS   

CREATE DATABASE IF NOT EXISTS healthlogger;
USE healthlogger;

CREATE TABLE IF NOT EXISTS users(
    user_id INT(64) NOT NULL AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL UNIQUE,
    PRIMARY KEY(user_id)
);

CREATE TABLE IF NOT EXISTS daily_data(
    entryid INT(64) NOT NULL AUTO_INCREMENT,
    entry_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    weight FLOAT,
    waist FLOAT,
    blood_preasure VARCHAR(25),
    mental_state VARCHAR,
    stress INT,
    PRIMARY KEY(entryid) 
);

CREATE TABLE IF NOT EXISTS diary(
    user_id INT(64) NOT NULL,
    entry_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    content TEXT NOT NULL

);

--The following table is like a memory-cache for the ai-agent so it can remember your previous conversations
CREATE TABLE IF NOT EXISTS ai_insights (
    insight_id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    query_hash VARCHAR(64),     
    user_query TEXT NOT NULL,    
    ai_response TEXT NOT NULL,  
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (insight_id),
    CONSTRAINT fk_user_insight FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB;