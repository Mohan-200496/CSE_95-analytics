"""
Quick fix for production enum values
Add to the jobs router to expose database enum information
"""

@router.get("/debug/database-enums")
async def get_database_enums(
    session: AsyncSession = Depends(get_database)
):
    """Get current enum values from production database"""
    try:
        # Query to get all enum types and their values
        enum_query = """
            SELECT t.typname, array_agg(e.enumlabel ORDER BY e.enumsortorder) as labels
            FROM pg_type t 
            JOIN pg_enum e ON t.oid = e.enumtypid 
            WHERE t.typname IN ('userrole', 'jobtype', 'jobstatus', 'accountstatus', 'employertype')
            GROUP BY t.typname
            ORDER BY t.typname;
        """
        
        result = await session.execute(text(enum_query))
        enums = result.fetchall()
        
        enum_data = {}
        for enum_type, labels in enums:
            enum_data[enum_type] = labels
        
        return {
            "success": True,
            "database_enums": enum_data,
            "python_enums": {
                "userrole": [role.value for role in UserRole],
                "jobtype": [job_type.value for job_type in JobType],
                "jobstatus": [status.value for status in JobStatus],
                "accountstatus": [status.value for status in AccountStatus],
                "employertype": [emp_type.value for emp_type in EmployerType]
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to query database enums"
        }

@router.post("/debug/fix-enums")
async def fix_database_enums(
    session: AsyncSession = Depends(get_database)
):
    """Add missing enum values to production database"""
    try:
        fixes_applied = []
        
        # Add missing userrole values
        userrole_fixes = [
            "ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'employer';",
            "ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'job_seeker';", 
            "ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'admin';",
            "ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'moderator';"
        ]
        
        # Add missing jobtype values  
        jobtype_fixes = [
            "ALTER TYPE jobtype ADD VALUE IF NOT EXISTS 'full_time';",
            "ALTER TYPE jobtype ADD VALUE IF NOT EXISTS 'part_time';",
            "ALTER TYPE jobtype ADD VALUE IF NOT EXISTS 'contract';",
            "ALTER TYPE jobtype ADD VALUE IF NOT EXISTS 'temporary';",
            "ALTER TYPE jobtype ADD VALUE IF NOT EXISTS 'internship';",
            "ALTER TYPE jobtype ADD VALUE IF NOT EXISTS 'freelance';"
        ]
        
        all_fixes = userrole_fixes + jobtype_fixes
        
        for fix_sql in all_fixes:
            try:
                await session.execute(text(fix_sql))
                fixes_applied.append(fix_sql)
            except Exception as e:
                # Log but continue with other fixes
                fixes_applied.append(f"FAILED: {fix_sql} - {str(e)}")
        
        await session.commit()
        
        return {
            "success": True,
            "message": f"Applied {len(fixes_applied)} enum fixes",
            "fixes_applied": fixes_applied
        }
        
    except Exception as e:
        await session.rollback()
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to fix database enums"
        }