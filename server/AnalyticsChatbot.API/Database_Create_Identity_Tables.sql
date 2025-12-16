-- Create Identity Database and Tables for ASP.NET Core Identity
-- Run this script in MySQL Workbench or via mysql command line

-- Create database
CREATE DATABASE IF NOT EXISTS chatbot_identity;
USE chatbot_identity;

-- AspNetRoles table
CREATE TABLE IF NOT EXISTS AspNetRoles (
    Id VARCHAR(255) NOT NULL PRIMARY KEY,
    Name VARCHAR(256) NULL,
    NormalizedName VARCHAR(256) NULL UNIQUE,
    ConcurrencyStamp TEXT NULL
);

-- AspNetUsers table
CREATE TABLE IF NOT EXISTS AspNetUsers (
    Id VARCHAR(255) NOT NULL PRIMARY KEY,
    UserName VARCHAR(256) NULL,
    NormalizedUserName VARCHAR(256) NULL UNIQUE,
    Email VARCHAR(256) NULL,
    NormalizedEmail VARCHAR(256) NULL,
    EmailConfirmed BOOLEAN NOT NULL DEFAULT FALSE,
    PasswordHash TEXT NULL,
    SecurityStamp TEXT NULL,
    ConcurrencyStamp TEXT NULL,
    PhoneNumber TEXT NULL,
    PhoneNumberConfirmed BOOLEAN NOT NULL DEFAULT FALSE,
    TwoFactorEnabled BOOLEAN NOT NULL DEFAULT FALSE,
    LockoutEnd DATETIME(6) NULL,
    LockoutEnabled BOOLEAN NOT NULL DEFAULT FALSE,
    AccessFailedCount INT NOT NULL DEFAULT 0
);

-- Create indexes for AspNetUsers
CREATE INDEX IF NOT EXISTS EmailIndex ON AspNetUsers (NormalizedEmail);

-- AspNetUserClaims table
CREATE TABLE IF NOT EXISTS AspNetUserClaims (
    Id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    UserId VARCHAR(255) NOT NULL,
    ClaimType TEXT NULL,
    ClaimValue TEXT NULL,
    FOREIGN KEY (UserId) REFERENCES AspNetUsers(Id) ON DELETE CASCADE
);

-- Create index for AspNetUserClaims
CREATE INDEX IF NOT EXISTS IX_AspNetUserClaims_UserId ON AspNetUserClaims (UserId);

-- AspNetUserLogins table
CREATE TABLE IF NOT EXISTS AspNetUserLogins (
    LoginProvider VARCHAR(128) NOT NULL,
    ProviderKey VARCHAR(128) NOT NULL,
    ProviderDisplayName TEXT NULL,
    UserId VARCHAR(255) NOT NULL,
    PRIMARY KEY (LoginProvider, ProviderKey),
    FOREIGN KEY (UserId) REFERENCES AspNetUsers(Id) ON DELETE CASCADE
);

-- Create index for AspNetUserLogins
CREATE INDEX IF NOT EXISTS IX_AspNetUserLogins_UserId ON AspNetUserLogins (UserId);

-- AspNetUserRoles table
CREATE TABLE IF NOT EXISTS AspNetUserRoles (
    UserId VARCHAR(255) NOT NULL,
    RoleId VARCHAR(255) NOT NULL,
    PRIMARY KEY (UserId, RoleId),
    FOREIGN KEY (UserId) REFERENCES AspNetUsers(Id) ON DELETE CASCADE,
    FOREIGN KEY (RoleId) REFERENCES AspNetRoles(Id) ON DELETE CASCADE
);

-- Create indexes for AspNetUserRoles
CREATE INDEX IF NOT EXISTS IX_AspNetUserRoles_RoleId ON AspNetUserRoles (RoleId);

-- AspNetUserTokens table
CREATE TABLE IF NOT EXISTS AspNetUserTokens (
    UserId VARCHAR(255) NOT NULL,
    LoginProvider VARCHAR(128) NOT NULL,
    Name VARCHAR(128) NOT NULL,
    Value TEXT NULL,
    PRIMARY KEY (UserId, LoginProvider, Name),
    FOREIGN KEY (UserId) REFERENCES AspNetUsers(Id) ON DELETE CASCADE
);

-- AspNetRoleClaims table
CREATE TABLE IF NOT EXISTS AspNetRoleClaims (
    Id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    RoleId VARCHAR(255) NOT NULL,
    ClaimType TEXT NULL,
    ClaimValue TEXT NULL,
    FOREIGN KEY (RoleId) REFERENCES AspNetRoles(Id) ON DELETE CASCADE
);

-- Create index for AspNetRoleClaims
CREATE INDEX IF NOT EXISTS IX_AspNetRoleClaims_RoleId ON AspNetRoleClaims (RoleId);

-- Verify tables were created
SELECT 'Database and tables created successfully!' as Status;
SHOW TABLES;

