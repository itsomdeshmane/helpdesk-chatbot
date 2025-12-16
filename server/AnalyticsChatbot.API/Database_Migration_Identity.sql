-- Database Migration Script for ASP.NET Core Identity
-- This creates the necessary tables for user authentication

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS chatbot_identity;
USE chatbot_identity;

-- Note: ASP.NET Core Identity will automatically create the required tables
-- when you run the application for the first time.
-- 
-- The following tables will be created automatically:
-- - AspNetUsers (user accounts)
-- - AspNetRoles (user roles)
-- - AspNetUserRoles (user-role associations)
-- - AspNetUserClaims (additional user claims like Name)
-- - AspNetUserLogins (external login providers)
-- - AspNetUserTokens (authentication tokens)
-- - AspNetRoleClaims (role claims)
--
-- To generate these tables, simply run the API application and it will
-- create them automatically via Entity Framework migrations.
--
-- Alternatively, you can run: dotnet ef database update
--
-- After the tables are created, you can register users via the /api/auth/register endpoint

