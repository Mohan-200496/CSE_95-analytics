#!/bin/bash

# Punjab Rozgar Portal - Quick Cloud Database Setup
# This script helps you quickly set up a cloud database and migrate your application

echo "🚀 Punjab Rozgar Portal - Cloud Database Quick Setup"
echo "======================================================"

# Function to setup Supabase (Recommended)
setup_supabase() {
    echo ""
    echo "🔵 Supabase Setup Instructions:"
    echo "1. Go to https://supabase.com and create account"
    echo "2. Create a new project"
    echo "3. Go to Settings > Database"
    echo "4. Copy the connection string (postgres://...)"
    echo "5. Replace [YOUR-PASSWORD] with your database password"
    echo ""
    echo "📝 Example connection string:"
    echo "postgresql://postgres:[YOUR-PASSWORD]@db.abc123def456.supabase.co:5432/postgres"
    echo ""
    read -p "Enter your Supabase connection string: " SUPABASE_URL
    
    if [[ ! -z "$SUPABASE_URL" ]]; then
        export CLOUD_DATABASE_URL="$SUPABASE_URL"
        echo "✅ Supabase URL set!"
        return 0
    else
        echo "❌ No URL provided"
        return 1
    fi
}

# Function to setup Render
setup_render() {
    echo ""
    echo "🟡 Render PostgreSQL Setup Instructions:"
    echo "1. Go to https://render.com and create account"
    echo "2. Create a new PostgreSQL service"
    echo "3. Copy the External Database URL"
    echo ""
    echo "📝 Example connection string:"
    echo "postgresql://username:password@hostname:5432/database_name"
    echo ""
    read -p "Enter your Render PostgreSQL URL: " RENDER_URL
    
    if [[ ! -z "$RENDER_URL" ]]; then
        export CLOUD_DATABASE_URL="$RENDER_URL"
        echo "✅ Render URL set!"
        return 0
    else
        echo "❌ No URL provided"
        return 1
    fi
}

# Function to setup Neon
setup_neon() {
    echo ""
    echo "🟣 Neon Setup Instructions:"
    echo "1. Go to https://neon.tech and create account"
    echo "2. Create a new database"
    echo "3. Copy the connection string from dashboard"
    echo ""
    echo "📝 Example connection string:"
    echo "postgresql://username:password@ep-abc-123.region.aws.neon.tech/database?sslmode=require"
    echo ""
    read -p "Enter your Neon connection string: " NEON_URL
    
    if [[ ! -z "$NEON_URL" ]]; then
        export CLOUD_DATABASE_URL="$NEON_URL"
        echo "✅ Neon URL set!"
        return 0
    else
        echo "❌ No URL provided"
        return 1
    fi
}

# Function to setup custom PostgreSQL
setup_custom() {
    echo ""
    echo "⚙️ Custom PostgreSQL Setup:"
    echo "Enter your PostgreSQL connection details:"
    echo ""
    read -p "Host (e.g., localhost, db.example.com): " DB_HOST
    read -p "Port (default 5432): " DB_PORT
    read -p "Database name: " DB_NAME
    read -p "Username: " DB_USER
    read -s -p "Password: " DB_PASS
    echo ""
    
    DB_PORT=${DB_PORT:-5432}
    
    if [[ ! -z "$DB_HOST" && ! -z "$DB_NAME" && ! -z "$DB_USER" && ! -z "$DB_PASS" ]]; then
        export CLOUD_DATABASE_URL="postgresql://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
        echo "✅ Custom PostgreSQL URL configured!"
        return 0
    else
        echo "❌ Missing required information"
        return 1
    fi
}

# Main menu
echo ""
echo "Choose your cloud database provider:"
echo "1) Supabase (Recommended - Free tier available)"
echo "2) Render (Good for hosting + database)"
echo "3) Neon (Serverless PostgreSQL)"
echo "4) Custom PostgreSQL"
echo "5) I already have a connection string"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1) setup_supabase ;;
    2) setup_render ;;
    3) setup_neon ;;
    4) setup_custom ;;
    5)
        echo ""
        read -p "Enter your PostgreSQL connection string: " CUSTOM_URL
        if [[ ! -z "$CUSTOM_URL" ]]; then
            export CLOUD_DATABASE_URL="$CUSTOM_URL"
            echo "✅ Connection string set!"
        else
            echo "❌ No URL provided"
            exit 1
        fi
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

# Check if URL is set
if [[ -z "$CLOUD_DATABASE_URL" ]]; then
    echo "❌ No database URL configured"
    exit 1
fi

# Run the Python migration script
echo ""
echo "🔄 Running database migration..."
python setup_cloud_database.py

if [[ $? -eq 0 ]]; then
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "📋 Your application is now configured to use cloud database:"
    echo "🔗 Database URL: ${CLOUD_DATABASE_URL:0:50}..."
    echo ""
    echo "🚀 Next steps:"
    echo "1. Restart your application"
    echo "2. Test the demo accounts:"
    echo "   • Admin: admin@test.com / admin123"
    echo "   • Employer: employer@test.com / employer123"
    echo "   • Job Seeker: jobseeker@email.com / jobseeker123"
    echo ""
    echo "💡 To make this permanent, add to your .env file:"
    echo "DATABASE_URL=$CLOUD_DATABASE_URL"
else
    echo ""
    echo "❌ Setup failed. Check the error messages above."
    exit 1
fi