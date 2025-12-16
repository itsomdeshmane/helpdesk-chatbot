# PowerShell script to setup MySQL databases
Write-Host "Setting up databases..." -ForegroundColor Green

# MySQL connection parameters
$mysqlPath = "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
$user = "root"
$password = "root123"
$hostname = "localhost"

# Check if MySQL is in common locations
$mysqlPaths = @(
    "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe",
    "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe",
    "C:\xampp\mysql\bin\mysql.exe",
    "C:\wamp64\bin\mysql\mysql8.0.27\bin\mysql.exe"
)

$mysqlExe = $null
foreach ($path in $mysqlPaths) {
    if (Test-Path $path) {
        $mysqlExe = $path
        Write-Host "Found MySQL at: $path" -ForegroundColor Cyan
        break
    }
}

if ($null -eq $mysqlExe) {
    Write-Host "MySQL not found in common locations. Please install MySQL or update the path in this script." -ForegroundColor Red
    Write-Host "Trying 'mysql' command from PATH..." -ForegroundColor Yellow
    $mysqlExe = "mysql"
}

# Execute SQL commands
Write-Host "`nCreating databases and tables..." -ForegroundColor Yellow

$sqlCommands = @"
-- Create databases
CREATE DATABASE IF NOT EXISTS chatbot_identity CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS erp_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Use Identity Database
USE chatbot_identity;

-- AspNetRoles
CREATE TABLE IF NOT EXISTS AspNetRoles (
    Id VARCHAR(255) NOT NULL PRIMARY KEY,
    Name VARCHAR(256) NULL,
    NormalizedName VARCHAR(256) NULL UNIQUE,
    ConcurrencyStamp TEXT NULL
) ENGINE=InnoDB;

-- AspNetUsers
CREATE TABLE IF NOT EXISTS AspNetUsers (
    Id VARCHAR(255) NOT NULL PRIMARY KEY,
    UserName VARCHAR(256) NULL,
    NormalizedUserName VARCHAR(256) NULL UNIQUE,
    Email VARCHAR(256) NULL,
    NormalizedEmail VARCHAR(256) NULL,
    EmailConfirmed TINYINT(1) NOT NULL DEFAULT 0,
    PasswordHash TEXT NULL,
    SecurityStamp TEXT NULL,
    ConcurrencyStamp TEXT NULL,
    PhoneNumber TEXT NULL,
    PhoneNumberConfirmed TINYINT(1) NOT NULL DEFAULT 0,
    TwoFactorEnabled TINYINT(1) NOT NULL DEFAULT 0,
    LockoutEnd DATETIME(6) NULL,
    LockoutEnabled TINYINT(1) NOT NULL DEFAULT 0,
    AccessFailedCount INT NOT NULL DEFAULT 0
) ENGINE=InnoDB;

-- AspNetUserRoles
CREATE TABLE IF NOT EXISTS AspNetUserRoles (
    UserId VARCHAR(255) NOT NULL,
    RoleId VARCHAR(255) NOT NULL,
    PRIMARY KEY (UserId, RoleId),
    FOREIGN KEY (UserId) REFERENCES AspNetUsers(Id) ON DELETE CASCADE,
    FOREIGN KEY (RoleId) REFERENCES AspNetRoles(Id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- AspNetUserClaims
CREATE TABLE IF NOT EXISTS AspNetUserClaims (
    Id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    UserId VARCHAR(255) NOT NULL,
    ClaimType TEXT NULL,
    ClaimValue TEXT NULL,
    FOREIGN KEY (UserId) REFERENCES AspNetUsers(Id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- AspNetUserLogins
CREATE TABLE IF NOT EXISTS AspNetUserLogins (
    LoginProvider VARCHAR(128) NOT NULL,
    ProviderKey VARCHAR(128) NOT NULL,
    ProviderDisplayName TEXT NULL,
    UserId VARCHAR(255) NOT NULL,
    PRIMARY KEY (LoginProvider, ProviderKey),
    FOREIGN KEY (UserId) REFERENCES AspNetUsers(Id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- AspNetUserTokens
CREATE TABLE IF NOT EXISTS AspNetUserTokens (
    UserId VARCHAR(255) NOT NULL,
    LoginProvider VARCHAR(128) NOT NULL,
    Name VARCHAR(128) NOT NULL,
    Value TEXT NULL,
    PRIMARY KEY (UserId, LoginProvider, Name),
    FOREIGN KEY (UserId) REFERENCES AspNetUsers(Id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- AspNetRoleClaims
CREATE TABLE IF NOT EXISTS AspNetRoleClaims (
    Id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    RoleId VARCHAR(255) NOT NULL,
    ClaimType TEXT NULL,
    ClaimValue TEXT NULL,
    FOREIGN KEY (RoleId) REFERENCES AspNetRoles(Id) ON DELETE CASCADE
) ENGINE=InnoDB;
"@

# Save SQL to temp file
$tempSqlFile = [System.IO.Path]::GetTempFileName() + ".sql"
$sqlCommands | Out-File -FilePath $tempSqlFile -Encoding UTF8

# Execute
try {
    & $mysqlExe -u $user -p$password -h $hostname -e "source $tempSqlFile"
    Write-Host "`nDatabases and tables created successfully!" -ForegroundColor Green
    
    # Verify
    Write-Host "`nVerifying setup..." -ForegroundColor Yellow
    & $mysqlExe -u $user -p$password -h $hostname -e "SHOW DATABASES LIKE 'chatbot%'; SHOW DATABASES LIKE 'erp%';"
    & $mysqlExe -u $user -p$password -h $hostname -D chatbot_identity -e "SHOW TABLES;"
    
    Write-Host "`n✅ Setup Complete!" -ForegroundColor Green
    Write-Host "You can now run your application with: dotnet run" -ForegroundColor Cyan
}
catch {
    Write-Host "`nError executing SQL: $_" -ForegroundColor Red
    Write-Host "Please run the SQL commands manually in MySQL Workbench or command line." -ForegroundColor Yellow
}
finally {
    # Cleanup temp file
    if (Test-Path $tempSqlFile) {
        Remove-Item $tempSqlFile
    }
}

