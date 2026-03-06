--This is the database for Healthlogger 2.0. It is using Mariadb as RDBMS   

CREATE DATABASE IF NOT EXISTS healthlogger;
USE healthlogger;

CREATE TABLE IF NOT EXISTS users(
    user_id INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(255) UNIQUE NOT NULL,
    passwd VARCHAR(255) NOT NULL,
    PRIMARY KEY(user_id)
);

CREATE TABLE IF NOT EXISTS daily_data(
    entryid INT NOT NULL AUTO_INCREMENT,
    entry_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    user_weight FLOAT,
    waist FLOAT,
    blood_pressure VARCHAR(25),
    mental_state VARCHAR(64),
    stress INT,
    PRIMARY KEY(entryid),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS diary(
    entry_id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    entry_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    content TEXT NOT NULL,
    PRIMARY KEY (entry_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

--The following table is like a memory-cache for the ai-agent so it can remember your previous conversations
CREATE TABLE IF NOT EXISTS ai_insights (
    insight_id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,    
    user_query TEXT NOT NULL,    
    ai_response TEXT NOT NULL,  
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (insight_id),
    CONSTRAINT fk_user_insight FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS knowledge_categories(
    category_id INT NOT NULL,
    category_name VARCHAR(255) NOT NULL,
    PRIMARY KEY(category_id)
);

CREATE TABLE IF NOT EXISTS knowledge_db(
    user_id INT NOT NULL, 
    category_id INT NOT NULL,
    knowledge_content TEXT NOT NULL,
    entry_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES knowledge_categories(category_id)
);

INSERT IGNORE INTO knowledge_categories (category_id, category_name) VALUES 
(1, 'Identity'), (2, 'Values'), (3, 'Goals'), (4, 'Health'), (5, 'Mental-Health'),
(6, 'Habits'), (7, 'Skills'), (8, 'Career'), (9, 'Finance'), (10, 'Technology'),
(11, 'Programming'), (12, 'Security'), (13, 'Nature'), (14, 'Fitness'), (15, 'Food & Nutrition'),
(16, 'Philosofy'), (17, 'Psychology'), (18, 'Relationships'), (19, 'Communication'), (20, 'Creativity'),
(21, 'Projects'), (22, 'Ideas'), (23, 'Observations'), (24, 'Lessons Learned'), (25, 'Random Facts');