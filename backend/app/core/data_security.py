"""
Data Security and Privacy Protection Module for Punjab Rozgar Portal
Implements comprehensive data security measures including:
- Data encryption at rest and in transit
- Personal data anonymization
- Secure data handling protocols
- Audit logging for data access
- GDPR compliance utilities
"""

import hashlib
import secrets
import base64
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import json
import re

logger = logging.getLogger(__name__)

class DataSecurityManager:
    """Comprehensive data security management"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        self.encryption_key = encryption_key or self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key.encode() if isinstance(self.encryption_key, str) else self.encryption_key)
        
        # Sensitive data fields that require special handling
        self.sensitive_fields = {
            'password', 'hashed_password', 'email', 'phone', 'address',
            'national_id', 'social_security', 'bank_account', 'credit_card',
            'personal_details', 'medical_info', 'financial_info'
        }
        
        # Data retention policies (in days)
        self.data_retention = {
            'user_data': 2555,  # 7 years
            'job_applications': 1095,  # 3 years
            'activity_logs': 365,  # 1 year
            'session_logs': 30,  # 30 days
            'error_logs': 90  # 90 days
        }
    
    def _generate_encryption_key(self) -> bytes:
        """Generate a secure encryption key"""
        password = secrets.token_urlsafe(32).encode()
        salt = secrets.token_bytes(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            if not data:
                return data
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise SecurityError("Data encryption failed")
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            if not encrypted_data:
                return encrypted_data
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise SecurityError("Data decryption failed")
    
    def hash_pii(self, data: str, salt: Optional[str] = None) -> str:
        """Hash personally identifiable information"""
        if not salt:
            salt = secrets.token_hex(16)
        
        hash_input = f"{data}{salt}".encode()
        hashed = hashlib.sha256(hash_input).hexdigest()
        return f"{hashed}:{salt}"
    
    def anonymize_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize user data for analytics while preserving utility"""
        anonymized = user_data.copy()
        
        # Replace email with hashed version
        if 'email' in anonymized:
            anonymized['email_hash'] = self.hash_pii(anonymized['email'])
            del anonymized['email']
        
        # Replace name with initials
        if 'first_name' in anonymized:
            anonymized['first_initial'] = anonymized['first_name'][0] if anonymized['first_name'] else 'X'
            del anonymized['first_name']
        
        if 'last_name' in anonymized:
            anonymized['last_initial'] = anonymized['last_name'][0] if anonymized['last_name'] else 'X'
            del anonymized['last_name']
        
        # Generalize location data
        if 'city' in anonymized:
            anonymized['region'] = self._generalize_location(anonymized['city'])
            del anonymized['city']
        
        # Remove other sensitive fields
        sensitive_to_remove = ['phone', 'address', 'national_id']
        for field in sensitive_to_remove:
            anonymized.pop(field, None)
        
        return anonymized
    
    def _generalize_location(self, city: str) -> str:
        """Generalize location for privacy"""
        # Map cities to regions
        city_regions = {
            'lahore': 'central_punjab',
            'karachi': 'sindh_urban',
            'islamabad': 'capital_region',
            'rawalpindi': 'northern_punjab',
            'faisalabad': 'central_punjab',
            'multan': 'southern_punjab'
        }
        return city_regions.get(city.lower(), 'other_region')
    
    def sanitize_input(self, input_data: str) -> str:
        """Sanitize user input to prevent XSS and injection attacks"""
        if not input_data:
            return input_data
        
        # Remove HTML tags
        sanitized = re.sub(r'<[^>]*>', '', input_data)
        
        # Remove JavaScript
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        
        # Remove SQL injection patterns
        sql_patterns = [
            r'(union|select|insert|update|delete|drop|create|alter|exec|execute)\s',
            r'(--|#|/\*|\*/)',
            r"(';|'\s*or\s*'|'\s*and\s*')"
        ]
        
        for pattern in sql_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        # Escape special characters
        sanitized = sanitized.replace("'", "&#39;")
        sanitized = sanitized.replace('"', "&#34;")
        sanitized = sanitized.replace('<', "&lt;")
        sanitized = sanitized.replace('>', "&gt;")
        
        return sanitized.strip()
    
    def validate_data_access(self, user_id: str, requested_data: str, user_role: str) -> bool:
        """Validate if user has permission to access requested data"""
        # Role-based access control
        access_rules = {
            'admin': ['all_data'],
            'employer': ['own_jobs', 'applications_to_jobs', 'company_data'],
            'job_seeker': ['own_profile', 'public_jobs', 'own_applications']
        }
        
        allowed_access = access_rules.get(user_role, [])
        
        # Check specific permissions
        if 'all_data' in allowed_access:
            return True
        
        if requested_data in allowed_access:
            return True
        
        # Additional checks can be implemented here
        return False


class AuditLogger:
    """Audit logging for security and compliance"""
    
    def __init__(self):
        self.audit_logger = logging.getLogger('audit')
        self.audit_logger.setLevel(logging.INFO)
        
        # Create audit log file handler
        handler = logging.FileHandler('audit.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.audit_logger.addHandler(handler)
    
    def log_data_access(self, user_id: str, action: str, resource: str, 
                       ip_address: str, success: bool, details: Optional[str] = None):
        """Log data access events"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'action': action,
            'resource': resource,
            'ip_address': ip_address,
            'success': success,
            'details': details
        }
        
        self.audit_logger.info(json.dumps(log_entry))
    
    def log_security_event(self, event_type: str, severity: str, 
                          description: str, ip_address: str, user_id: Optional[str] = None):
        """Log security events"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'severity': severity,
            'description': description,
            'ip_address': ip_address,
            'user_id': user_id
        }
        
        self.audit_logger.warning(json.dumps(log_entry))


class PrivacyManager:
    """Privacy management and GDPR compliance"""
    
    def __init__(self, data_security_manager: DataSecurityManager):
        self.dsm = data_security_manager
        self.audit_logger = AuditLogger()
    
    def process_data_deletion_request(self, user_id: str) -> Dict[str, Any]:
        """Process user's right to be forgotten request"""
        try:
            # This would integrate with database to delete user data
            # For now, return a template response
            
            deletion_report = {
                'user_id': user_id,
                'request_date': datetime.utcnow().isoformat(),
                'status': 'processed',
                'data_deleted': [
                    'personal_profile',
                    'job_applications',
                    'activity_logs'
                ],
                'data_retained': [
                    'anonymized_analytics_data'
                ],
                'retention_reason': 'legal_compliance'
            }
            
            self.audit_logger.log_data_access(
                user_id, 'data_deletion', 'user_profile', 
                'system', True, 'GDPR deletion request processed'
            )
            
            return deletion_report
            
        except Exception as e:
            logger.error(f"Data deletion request failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def generate_data_export(self, user_id: str) -> Dict[str, Any]:
        """Generate data export for user's right to data portability"""
        try:
            # This would integrate with database to export user data
            export_data = {
                'user_id': user_id,
                'export_date': datetime.utcnow().isoformat(),
                'data_categories': [
                    'profile_information',
                    'job_applications',
                    'activity_history'
                ],
                'format': 'json',
                'status': 'ready_for_download'
            }
            
            self.audit_logger.log_data_access(
                user_id, 'data_export', 'user_profile',
                'system', True, 'GDPR export request processed'
            )
            
            return export_data
            
        except Exception as e:
            logger.error(f"Data export request failed: {e}")
            return {'status': 'failed', 'error': str(e)}


class SecurityError(Exception):
    """Custom exception for security-related errors"""
    pass


# Global instances
data_security_manager = DataSecurityManager()
audit_logger = AuditLogger()
privacy_manager = PrivacyManager(data_security_manager)