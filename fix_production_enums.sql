-- Fix PostgreSQL enum values for production database
-- This script updates the enum types to match the Python model definitions

-- First, let's see what enum values exist
-- SELECT enumlabel FROM pg_enum WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'jobtype');
-- SELECT enumlabel FROM pg_enum WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'userrole');

-- Drop and recreate the enum types with correct values
BEGIN;

-- Create temporary types with correct values
DO $$
BEGIN
    -- Create new jobtype enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'jobtype_new') THEN
        CREATE TYPE jobtype_new AS ENUM (
            'full_time',
            'part_time', 
            'contract',
            'temporary',
            'internship',
            'freelance'
        );
    END IF;
    
    -- Create new userrole enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole_new') THEN
        CREATE TYPE userrole_new AS ENUM (
            'job_seeker',
            'employer',
            'admin', 
            'moderator'
        );
    END IF;
    
    -- Create new jobstatus enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'jobstatus_new') THEN
        CREATE TYPE jobstatus_new AS ENUM (
            'draft',
            'pending_approval',
            'active',
            'paused',
            'closed',
            'expired'
        );
    END IF;
    
    -- Create new accountstatus enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'accountstatus_new') THEN
        CREATE TYPE accountstatus_new AS ENUM (
            'active',
            'inactive', 
            'suspended',
            'pending_verification'
        );
    END IF;
    
    -- Create new employertype enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'employertype_new') THEN
        CREATE TYPE employertype_new AS ENUM (
            'government',
            'public_sector',
            'private',
            'ngo',
            'startup'
        );
    END IF;
END $$;

-- Update tables to use new enum types (if tables exist)
DO $$
BEGIN
    -- Update jobs table
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'jobs') THEN
        -- Add new columns with correct enum types
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'jobs' AND column_name = 'job_type_new') THEN
            ALTER TABLE jobs ADD COLUMN job_type_new jobtype_new;
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'jobs' AND column_name = 'status_new') THEN
            ALTER TABLE jobs ADD COLUMN status_new jobstatus_new;
        END IF;
        
        -- Copy data with proper mapping
        UPDATE jobs SET 
            job_type_new = CASE 
                WHEN job_type::text = 'FULL_TIME' OR job_type::text = 'full-time' THEN 'full_time'::jobtype_new
                WHEN job_type::text = 'PART_TIME' OR job_type::text = 'part-time' THEN 'part_time'::jobtype_new
                WHEN job_type::text = 'CONTRACT' THEN 'contract'::jobtype_new
                WHEN job_type::text = 'TEMPORARY' THEN 'temporary'::jobtype_new
                WHEN job_type::text = 'INTERNSHIP' THEN 'internship'::jobtype_new
                WHEN job_type::text = 'FREELANCE' THEN 'freelance'::jobtype_new
                ELSE 'full_time'::jobtype_new
            END,
            status_new = CASE
                WHEN status::text = 'DRAFT' THEN 'draft'::jobstatus_new
                WHEN status::text = 'PENDING_APPROVAL' OR status::text = 'pending-approval' THEN 'pending_approval'::jobstatus_new
                WHEN status::text = 'ACTIVE' THEN 'active'::jobstatus_new
                WHEN status::text = 'PAUSED' THEN 'paused'::jobstatus_new
                WHEN status::text = 'CLOSED' THEN 'closed'::jobstatus_new
                WHEN status::text = 'EXPIRED' THEN 'expired'::jobstatus_new
                ELSE 'active'::jobstatus_new
            END;
    END IF;
    
    -- Update users table
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'role_new') THEN
            ALTER TABLE users ADD COLUMN role_new userrole_new;
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'status_new') THEN
            ALTER TABLE users ADD COLUMN status_new accountstatus_new;
        END IF;
        
        UPDATE users SET 
            role_new = CASE
                WHEN role::text = 'JOB_SEEKER' OR role::text = 'job-seeker' OR role::text = 'jobseeker' THEN 'job_seeker'::userrole_new
                WHEN role::text = 'EMPLOYER' THEN 'employer'::userrole_new
                WHEN role::text = 'ADMIN' THEN 'admin'::userrole_new
                WHEN role::text = 'MODERATOR' THEN 'moderator'::userrole_new
                ELSE 'job_seeker'::userrole_new
            END,
            status_new = CASE
                WHEN status::text = 'ACTIVE' THEN 'active'::accountstatus_new
                WHEN status::text = 'INACTIVE' THEN 'inactive'::accountstatus_new
                WHEN status::text = 'SUSPENDED' THEN 'suspended'::accountstatus_new
                WHEN status::text = 'PENDING_VERIFICATION' OR status::text = 'pending-verification' THEN 'pending_verification'::accountstatus_new
                ELSE 'pending_verification'::accountstatus_new
            END;
    END IF;
END $$;

COMMIT;

-- Instructions for completing the migration:
-- 1. Drop old enum columns: ALTER TABLE jobs DROP COLUMN job_type, DROP COLUMN status;
-- 2. Rename new columns: ALTER TABLE jobs RENAME COLUMN job_type_new TO job_type;
-- 3. Repeat for users table and other tables as needed
-- 4. Drop old enum types: DROP TYPE IF EXISTS old_jobtype_enum_name;

-- Note: This script is safe to run multiple times