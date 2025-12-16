-- Database Migration Script for Chat Sessions and Messages
-- Run this script to create tables for storing chat history

USE chatbot_identity;

-- Create ChatSessions table
CREATE TABLE IF NOT EXISTS ChatSessions (
    SessionId VARCHAR(255) NOT NULL PRIMARY KEY,
    UserId VARCHAR(255) NOT NULL,
    UserEmail VARCHAR(256) NULL,
    UserName VARCHAR(256) NULL,
    CreatedAt DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    IsActive BOOLEAN NOT NULL DEFAULT TRUE,
    MessageCount INT NOT NULL DEFAULT 0,
    INDEX IX_ChatSessions_UserId (UserId),
    INDEX IX_ChatSessions_CreatedAt (CreatedAt)
);

-- Create ChatMessages table
CREATE TABLE IF NOT EXISTS ChatMessages (
    MessageId VARCHAR(255) NOT NULL PRIMARY KEY,
    SessionId VARCHAR(255) NOT NULL,
    Message TEXT NOT NULL,
    Role VARCHAR(50) NOT NULL,
    SqlQuery TEXT NULL,
    ResponseData TEXT NULL,
    ResponseFormat VARCHAR(50) NULL,
    HasError BOOLEAN NOT NULL DEFAULT FALSE,
    ErrorMessage TEXT NULL,
    Timestamp DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    ResponseTimeMs INT NULL,
    INDEX IX_ChatMessages_SessionId (SessionId),
    INDEX IX_ChatMessages_Timestamp (Timestamp),
    FOREIGN KEY (SessionId) REFERENCES ChatSessions(SessionId) ON DELETE CASCADE
);

-- Verify tables were created
SELECT 'Chat session tables created successfully!' as Status;
SHOW TABLES LIKE 'Chat%';

-- Show table structure
DESCRIBE ChatSessions;
DESCRIBE ChatMessages;

