# Punjab Rozgar Portal - Cloud Database Setup (Windows)
# This PowerShell script helps you quickly set up a cloud database

Write-Host "🚀 Punjab Rozgar Portal - Cloud Database Quick Setup" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green

function Setup-Supabase {
    Write-Host ""
    Write-Host "🔵 Supabase Setup Instructions:" -ForegroundColor Blue
    Write-Host "1. Go to https://supabase.com and create account"
    Write-Host "2. Create a new project"
    Write-Host "3. Go to Settings > Database"
    Write-Host "4. Copy the connection string (postgres://...)"
    Write-Host "5. Replace [YOUR-PASSWORD] with your database password"
    Write-Host ""
    Write-Host "📝 Example connection string:" -ForegroundColor Yellow
    Write-Host "postgresql://postgres:[YOUR-PASSWORD]@db.abc123def456.supabase.co:5432/postgres"
    Write-Host ""
    $supabaseUrl = Read-Host "Enter your Supabase connection string"
    
    if ($supabaseUrl) {
        $env:CLOUD_DATABASE_URL = $supabaseUrl
        Write-Host "✅ Supabase URL set!" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ No URL provided" -ForegroundColor Red
        return $false
    }
}

function Setup-Render {
    Write-Host ""
    Write-Host "🟡 Render PostgreSQL Setup Instructions:" -ForegroundColor Yellow
    Write-Host "1. Go to https://render.com and create account"
    Write-Host "2. Create a new PostgreSQL service"
    Write-Host "3. Copy the External Database URL"
    Write-Host ""
    Write-Host "📝 Example connection string:" -ForegroundColor Yellow
    Write-Host "postgresql://username:password@hostname:5432/database_name"
    Write-Host ""
    $renderUrl = Read-Host "Enter your Render PostgreSQL URL"
    
    if ($renderUrl) {
        $env:CLOUD_DATABASE_URL = $renderUrl
        Write-Host "✅ Render URL set!" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ No URL provided" -ForegroundColor Red
        return $false
    }
}

function Setup-Neon {
    Write-Host ""
    Write-Host "🟣 Neon Setup Instructions:" -ForegroundColor Magenta
    Write-Host "1. Go to https://neon.tech and create account"
    Write-Host "2. Create a new database"
    Write-Host "3. Copy the connection string from dashboard"
    Write-Host ""
    Write-Host "📝 Example connection string:" -ForegroundColor Yellow
    Write-Host "postgresql://username:password@ep-abc-123.region.aws.neon.tech/database?sslmode=require"
    Write-Host ""
    $neonUrl = Read-Host "Enter your Neon connection string"
    
    if ($neonUrl) {
        $env:CLOUD_DATABASE_URL = $neonUrl
        Write-Host "✅ Neon URL set!" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ No URL provided" -ForegroundColor Red
        return $false
    }
}

function Setup-Custom {
    Write-Host ""
    Write-Host "⚙️ Custom PostgreSQL Setup:" -ForegroundColor Cyan
    Write-Host "Enter your PostgreSQL connection details:"
    Write-Host ""
    $dbHost = Read-Host "Host (e.g., localhost, db.example.com)"
    $dbPort = Read-Host "Port (default 5432)"
    $dbName = Read-Host "Database name"
    $dbUser = Read-Host "Username"
    $dbPass = Read-Host "Password" -AsSecureString
    
    # Convert secure string to plain text
    $dbPassPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($dbPass))
    
    if (-not $dbPort) { $dbPort = "5432" }
    
    if ($dbHost -and $dbName -and $dbUser -and $dbPassPlain) {
        $env:CLOUD_DATABASE_URL = "postgresql://${dbUser}:${dbPassPlain}@${dbHost}:${dbPort}/${dbName}"
        Write-Host "✅ Custom PostgreSQL URL configured!" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ Missing required information" -ForegroundColor Red
        return $false
    }
}

# Main menu
Write-Host ""
Write-Host "Choose your cloud database provider:" -ForegroundColor Cyan
Write-Host "1) Supabase (Recommended - Free tier available)"
Write-Host "2) Render (Good for hosting + database)"
Write-Host "3) Neon (Serverless PostgreSQL)"
Write-Host "4) Custom PostgreSQL"
Write-Host "5) I already have a connection string"
Write-Host ""
$choice = Read-Host "Enter your choice (1-5)"

$success = $false
switch ($choice) {
    "1" { $success = Setup-Supabase }
    "2" { $success = Setup-Render }
    "3" { $success = Setup-Neon }
    "4" { $success = Setup-Custom }
    "5" {
        Write-Host ""
        $customUrl = Read-Host "Enter your PostgreSQL connection string"
        if ($customUrl) {
            $env:CLOUD_DATABASE_URL = $customUrl
            Write-Host "✅ Connection string set!" -ForegroundColor Green
            $success = $true
        } else {
            Write-Host "❌ No URL provided" -ForegroundColor Red
            $success = $false
        }
    }
    default {
        Write-Host "❌ Invalid choice" -ForegroundColor Red
        exit 1
    }
}

# Check if URL is set
if (-not $success -or -not $env:CLOUD_DATABASE_URL) {
    Write-Host "❌ No database URL configured" -ForegroundColor Red
    exit 1
}

# Run the Python migration script
Write-Host ""
Write-Host "🔄 Running database migration..." -ForegroundColor Yellow
python setup_cloud_database.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "🎉 Setup completed successfully!" -ForegroundColor Green
    Write-Host ""
    $urlPreview = $env:CLOUD_DATABASE_URL.Substring(0, [Math]::Min(50, $env:CLOUD_DATABASE_URL.Length))
    Write-Host "📋 Your application is now configured to use cloud database:" -ForegroundColor Cyan
    Write-Host "🔗 Database URL: $urlPreview..." -ForegroundColor Gray
    Write-Host ""
    Write-Host "🚀 Next steps:" -ForegroundColor Cyan
    Write-Host "1. Restart your application"
    Write-Host "2. Test the demo accounts:"
    Write-Host "   • Admin: admin@test.com / admin123"
    Write-Host "   • Employer: employer@test.com / employer123"
    Write-Host "   • Job Seeker: jobseeker@email.com / jobseeker123"
    Write-Host ""
    Write-Host "💡 To make this permanent, add to your .env file:" -ForegroundColor Yellow
    Write-Host "DATABASE_URL=$($env:CLOUD_DATABASE_URL)"
} else {
    Write-Host ""
    Write-Host "❌ Setup failed. Check the error messages above." -ForegroundColor Red
    exit 1
}