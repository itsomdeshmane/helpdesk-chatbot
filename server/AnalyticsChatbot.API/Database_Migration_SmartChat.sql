-- Smart RAG Chatbot Database Tables
-- Run this script to create the required tables for the Smart Chat feature

USE erp_identity; -- or your identity database name

-- Table to store conversation history
CREATE TABLE IF NOT EXISTS ConversationHistories (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    UserId VARCHAR(255) NOT NULL,
    SessionId VARCHAR(255) NOT NULL,
    Message TEXT NOT NULL,
    Role VARCHAR(50) NOT NULL, -- 'user' or 'assistant'
    Intent VARCHAR(255) NULL,
    Keywords TEXT NULL, -- Comma-separated keywords
    Context TEXT NULL, -- JSON string
    ConfidenceScore FLOAT NULL,
    IsClarity BOOLEAN DEFAULT FALSE,
    Timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Metadata TEXT NULL,
    INDEX idx_user_session (UserId, SessionId),
    INDEX idx_timestamp (Timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table to store knowledge base (Q&A pairs)
CREATE TABLE IF NOT EXISTS KnowledgeBases (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    Question TEXT NOT NULL,
    Answer TEXT NOT NULL,
    Keywords TEXT NULL,
    Category VARCHAR(255) NULL,
    Embedding LONGTEXT NULL, -- JSON array of embedding vector
    UsageCount INT DEFAULT 0,
    AverageConfidence FLOAT DEFAULT 0,
    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt DATETIME NULL,
    INDEX idx_category (Category),
    INDEX idx_usage (UsageCount DESC),
    FULLTEXT idx_question (Question),
    FULLTEXT idx_answer (Answer)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table to store conversation context
CREATE TABLE IF NOT EXISTS ConversationContexts (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    SessionId VARCHAR(255) NOT NULL,
    UserId VARCHAR(255) NOT NULL,
    CurrentIntent VARCHAR(255) NULL,
    PendingClarification TEXT NULL,
    ContextData TEXT NULL, -- JSON
    LastActivity DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    IsActive BOOLEAN DEFAULT TRUE,
    UNIQUE INDEX idx_session_user (SessionId, UserId),
    INDEX idx_last_activity (LastActivity)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Optional: Sample knowledge base entries
INSERT INTO KnowledgeBases (Question, Answer, Category, Keywords) VALUES
('What is ERP?', 'ERP stands for Enterprise Resource Planning. It is a type of software that organizations use to manage day-to-day business activities such as accounting, procurement, project management, and manufacturing.', 'definitions', 'erp,enterprise,resource,planning,software'),
('How do I generate a report?', 'You can generate reports by using natural language queries. Simply ask me questions about your data, and I will create SQL queries and present the results in various formats.', 'how-to', 'generate,report,create,query'),
('What types of data can I query?', 'You can query various types of data including vendors, customers, products, orders, sales, employees, and more. Just ask your question in plain English.', 'capabilities', 'query,data,types,information');

-- Check if tables were created successfully
SELECT 'Tables created successfully!' AS Status;
SELECT COUNT(*) AS ConversationHistories_Exists FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'ConversationHistories';
SELECT COUNT(*) AS KnowledgeBases_Exists FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'KnowledgeBases';
SELECT COUNT(*) AS ConversationContexts_Exists FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'ConversationContexts';

