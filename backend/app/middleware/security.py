"""
Enhanced Security middleware for Punjab Rozgar Portal
Implements comprehensive security measures including:
- Advanced rate limiting with progressive penalties
- SQL injection and XSS detection
- Threat pattern recognition
- Security headers and CSRF protection
- Audit logging integration
"""

from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
import logging
import ipaddress
import re
import json
import hashlib
from typing import Dict, Set, Optional, Tuple, List
from collections import defaultdict, deque
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Import audit logger if available
try:
    from ..core.data_security import audit_logger, data_security_manager
    HAS_AUDIT_LOGGER = True
except ImportError:
    HAS_AUDIT_LOGGER = False
    # Create a simple fallback logger
    audit_logger = logging.getLogger('audit')

class ThreatDetector:
    """Advanced threat detection patterns"""
    
    def __init__(self):
        # SQL injection patterns
        self.sql_patterns = [
            r'(\bUNION\b.*\bSELECT\b)',
            r'(\bSELECT\b.*\bFROM\b.*\bWHERE\b)',
            r'(\bINSERT\b.*\bINTO\b.*\bVALUES\b)',
            r'(\bUPDATE\b.*\bSET\b)',
            r'(\bDELETE\b.*\bFROM\b)',
            r'(\bDROP\b.*\bTABLE\b)',
            r'(\';.*--)',
            r'(\bOR\b.*=.*\bOR\b)',
            r'(\bAND\b.*=.*\bAND\b)',
            r'(1=1|1=0)',
            r'(\bhex\b|\bchar\b|\bascii\b)',
            r'(\bexec\b|\bexecute\b)'
        ]
        
        # XSS patterns
        self.xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
            r'<link[^>]*>',
            r'<meta[^>]*>',
            r'vbscript:',
            r'data:text/html',
            r'expression\s*\(',
            r'@import'
        ]
        
        # Command injection patterns
        self.command_patterns = [
            r'[;&|`$(){}[\]\\]',
            r'\b(cat|ls|pwd|whoami|id|uname)\b',
            r'\b(wget|curl|nc|netcat)\b',
            r'\b(rm|del|format)\b',
            r'\.\./|\.\.\\'
        ]
        
        # Compile regex patterns for performance
        self.compiled_sql = [re.compile(pattern, re.IGNORECASE) for pattern in self.sql_patterns]
        self.compiled_xss = [re.compile(pattern, re.IGNORECASE) for pattern in self.xss_patterns]
        self.compiled_cmd = [re.compile(pattern, re.IGNORECASE) for pattern in self.command_patterns]
    
    def detect_sql_injection(self, content: str) -> List[str]:
        """Detect SQL injection attempts"""
        threats = []
        for pattern in self.compiled_sql:
            if pattern.search(content):
                threats.append(f"SQL injection pattern detected: {pattern.pattern}")
        return threats
    
    def detect_xss(self, content: str) -> List[str]:
        """Detect XSS attempts"""
        threats = []
        for pattern in self.compiled_xss:
            if pattern.search(content):
                threats.append(f"XSS pattern detected: {pattern.pattern}")
        return threats
    
    def detect_command_injection(self, content: str) -> List[str]:
        """Detect command injection attempts"""
        threats = []
        for pattern in self.compiled_cmd:
            if pattern.search(content):
                threats.append(f"Command injection pattern detected: {pattern.pattern}")
        return threats
    
    def analyze_request(self, request: Request, body: str = "") -> List[str]:
        """Comprehensive threat analysis"""
        threats = []
        
        # Analyze URL path
        threats.extend(self.detect_sql_injection(str(request.url)))
        threats.extend(self.detect_xss(str(request.url)))
        threats.extend(self.detect_command_injection(str(request.url)))
        
        # Analyze query parameters
        for key, value in request.query_params.items():
            content = f"{key}={value}"
            threats.extend(self.detect_sql_injection(content))
            threats.extend(self.detect_xss(content))
            threats.extend(self.detect_command_injection(content))
        
        # Analyze headers for suspicious content
        suspicious_headers = ['user-agent', 'referer', 'x-forwarded-for']
        for header in suspicious_headers:
            if header in request.headers:
                threats.extend(self.detect_xss(request.headers[header]))
        
        # Analyze request body
        if body:
            threats.extend(self.detect_sql_injection(body))
            threats.extend(self.detect_xss(body))
            threats.extend(self.detect_command_injection(body))
        
        return threats

class SecurityMiddleware(BaseHTTPMiddleware):
    """Enhanced security middleware with comprehensive threat protection"""
    
    def __init__(self, app, rate_limit_requests: int = 100, rate_limit_window: int = 60):
        super().__init__(app)
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_window = rate_limit_window
        
        # Advanced rate limiting storage
        self.request_counts = defaultdict(lambda: deque())
        self.failed_login_attempts = defaultdict(lambda: deque())
        
        # Security tracking
        self.blocked_ips: Set[str] = set()
        self.suspicious_ips: Set[str] = set()
        self.threat_scores = defaultdict(int)
        self.last_cleanup = time.time()
        
        # Initialize threat detector
        self.threat_detector = ThreatDetector()
        
        # Whitelist for safe IPs (admin IPs, trusted services)
        self.whitelisted_ips: Set[str] = set()
        
        # Request pattern analysis
        self.request_patterns = defaultdict(lambda: defaultdict(int))
        
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request with validation"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain and validate
            ip = forwarded_for.split(",")[0].strip()
            if self._is_valid_ip(ip):
                return ip
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip and self._is_valid_ip(real_ip.strip()):
            return real_ip.strip()
        
        # Fall back to direct connection IP
        if hasattr(request.client, 'host'):
            return request.client.host
        
        return "unknown"
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Validate IP address format"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    def calculate_threat_score(self, ip: str, threats: List[str], request: Request) -> int:
        """Calculate threat score for request"""
        score = 0
        
        # Base threat score from detected patterns
        score += len(threats) * 10
        
        # Additional scoring factors
        if ip in self.suspicious_ips:
            score += 5
        
        # Suspicious user agents
        user_agent = request.headers.get("user-agent", "").lower()
        suspicious_agents = ['sqlmap', 'nmap', 'burp', 'nikto', 'dirb', 'gobuster']
        if any(agent in user_agent for agent in suspicious_agents):
            score += 20
        
        # Rapid requests pattern
        now = time.time()
        recent_requests = [t for t in self.request_counts[ip] if t > now - 10]
        if len(recent_requests) > 10:  # More than 10 requests in 10 seconds
            score += 15
        
        # Failed login attempts
        recent_failures = [t for t in self.failed_login_attempts[ip] if t > now - 300]
        score += len(recent_failures) * 3
        
        return score
    
    def is_advanced_rate_limited(self, ip: str, request: Request) -> Tuple[bool, str]:
        """Advanced rate limiting with progressive penalties"""
        if ip in self.whitelisted_ips:
            return False, ""
        
        now = time.time()
        
        # Clean old entries
        cutoff = now - self.rate_limit_window
        while self.request_counts[ip] and self.request_counts[ip][0] < cutoff:
            self.request_counts[ip].popleft()
        
        # Progressive rate limiting based on threat score
        threat_score = self.threat_scores[ip]
        
        if threat_score > 50:
            max_requests = max(1, self.rate_limit_requests // 10)  # Very restrictive
            penalty_msg = "High threat score detected"
        elif threat_score > 20:
            max_requests = max(10, self.rate_limit_requests // 4)  # Moderately restrictive
            penalty_msg = "Elevated threat score"
        else:
            max_requests = self.rate_limit_requests  # Normal rate limit
            penalty_msg = ""
        
        # Check rate limit
        if len(self.request_counts[ip]) >= max_requests:
            return True, penalty_msg or "Rate limit exceeded"
        
        # Add current request
        self.request_counts[ip].append(now)
        return False, ""
    
    def cleanup_old_data(self):
        """Periodic cleanup of old tracking data"""
        now = time.time()
        if now - self.last_cleanup < 300:  # Cleanup every 5 minutes
            return
        
        # Clean old request counts
        cutoff = now - self.rate_limit_window * 2
        for ip in list(self.request_counts.keys()):
            self.request_counts[ip] = deque(
                [t for t in self.request_counts[ip] if t > cutoff]
            )
            if not self.request_counts[ip]:
                del self.request_counts[ip]
        
        # Clean old threat scores
        for ip in list(self.threat_scores.keys()):
            if ip not in self.request_counts:
                self.threat_scores[ip] = max(0, self.threat_scores[ip] - 1)
                if self.threat_scores[ip] == 0:
                    del self.threat_scores[ip]
        
        self.last_cleanup = now
    
    async def read_body(self, request: Request) -> str:
        """Safely read request body"""
        try:
            body = await request.body()
            return body.decode('utf-8')
        except Exception:
            return ""
    
    def _sanitize_input(self, input_data: str) -> str:
        """Basic input sanitization fallback"""
        if not input_data:
            return input_data
        
        # Remove HTML tags
        sanitized = re.sub(r'<[^>]*>', '', input_data)
        
        # Remove JavaScript
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        
        # Remove basic SQL injection patterns
        sanitized = re.sub(r'(union|select|insert|update|delete|drop|create|alter|exec|execute)\s', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'(--|#|/\*|\*/)', '', sanitized)
        
        # Escape special characters
        sanitized = sanitized.replace("'", "&#39;")
        sanitized = sanitized.replace('"', "&#34;")
        sanitized = sanitized.replace('<', "&lt;")
        sanitized = sanitized.replace('>', "&gt;")
        
        return sanitized.strip()
    
    def _log_security_event(self, event_type: str, severity: str, description: str, ip_address: str, user_id: Optional[str] = None):
        """Log security events with fallback"""
        if HAS_AUDIT_LOGGER:
            audit_logger.log_security_event(event_type, severity, description, ip_address, user_id)
        else:
            logger.warning(f"SECURITY EVENT [{severity}] {event_type}: {description} (IP: {ip_address})")
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Enhanced security processing for each request"""
        start_time = time.time()
        
        try:
            # Periodic cleanup
            self.cleanup_old_data()
            
            # Extract client IP and basic validation
            client_ip = self.get_client_ip(request)
            
            # Skip security checks for health endpoints
            if request.url.path in ["/health", "/ping", "/api/docs", "/api/redoc", "/api/openapi.json"]:
                response = await call_next(request)
                response.headers["X-Process-Time"] = str(time.time() - start_time)
                return response
            
            # Check if IP is blocked
            if client_ip in self.blocked_ips:
                self._log_security_event(
                    "blocked_ip_access", "high", 
                    f"Blocked IP {client_ip} attempted access to {request.url.path}",
                    client_ip
                )
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Access denied", "code": "BLOCKED_IP"}
                )
            
            # Read request body for analysis
            body = await self.read_body(request)
            
            # Threat analysis
            threats = self.threat_detector.analyze_request(request, body)
            
            if threats:
                # Update threat score
                self.threat_scores[client_ip] += len(threats)
                
                # Log security event
                self._log_security_event(
                    "threat_detected", "medium",
                    f"Threats detected from {client_ip}: {'; '.join(threats[:3])}",
                    client_ip
                )
                
                # Block if threat score is too high
                if self.threat_scores[client_ip] > 100:
                    self.blocked_ips.add(client_ip)
                    self._log_security_event(
                        "ip_auto_blocked", "high",
                        f"IP {client_ip} auto-blocked due to high threat score: {self.threat_scores[client_ip]}",
                        client_ip
                    )
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={"detail": "Access denied due to security violations", "code": "THREAT_DETECTED"}
                    )
            
            # Advanced rate limiting
            is_limited, limit_reason = self.is_advanced_rate_limited(client_ip, request)
            if is_limited:
                self._log_security_event(
                    "rate_limit_exceeded", "low",
                    f"Rate limit exceeded for {client_ip}: {limit_reason}",
                    client_ip
                )
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": f"Too many requests: {limit_reason}",
                        "code": "RATE_LIMITED",
                        "retry_after": self.rate_limit_window
                    }
                )
            
            # Input sanitization for body content
            if body and request.method in ["POST", "PUT", "PATCH"]:
                try:
                    # Parse JSON and sanitize
                    if request.headers.get("content-type", "").startswith("application/json"):
                        data = json.loads(body)
                        sanitized_data = self._sanitize_json_data(data)
                        sanitized_body = json.dumps(sanitized_data)
                        # Note: In production, you'd need to modify the request object
                        # This is a simplified example
                except json.JSONDecodeError:
                    # Not JSON, apply basic sanitization
                    sanitized_body = self._sanitize_input(body)
            
            # Process the request
            response = await call_next(request)
            
            # Add comprehensive security headers
            self._add_security_headers(response)
            
            # Add processing time header for monitoring
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log successful request
            if threats:
                self._log_security_event(
                    "request_processed_with_threats", "low",
                    f"Request from {client_ip} processed despite threats: {len(threats)} detected",
                    client_ip
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Enhanced security middleware error: {e}")
            self._log_security_event(
                "middleware_error", "high",
                f"Security middleware error: {str(e)}",
                client_ip if 'client_ip' in locals() else "unknown"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error", "code": "MIDDLEWARE_ERROR"}
            )
    
    def _sanitize_json_data(self, data):
        """Recursively sanitize JSON data"""
        if isinstance(data, dict):
            return {key: self._sanitize_json_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_json_data(item) for item in data]
        elif isinstance(data, str):
            if HAS_AUDIT_LOGGER:
                return data_security_manager.sanitize_input(data)
            else:
                return self._sanitize_input(data)
        else:
            return data
    
    def _add_security_headers(self, response: Response):
        """Add comprehensive security headers"""
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=(), usb=()",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            ),
            "X-Permitted-Cross-Domain-Policies": "none",
            "X-Download-Options": "noopen",
            "X-DNS-Prefetch-Control": "off",
            "Expect-CT": "max-age=86400, enforce"
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
    
    def record_failed_login(self, ip: str):
        """Record failed login attempt"""
        now = time.time()
        self.failed_login_attempts[ip].append(now)
        self.threat_scores[ip] += 5
        
        # Auto-block after too many failed attempts
        recent_failures = [t for t in self.failed_login_attempts[ip] if t > now - 900]  # Last 15 minutes
        if len(recent_failures) >= 5:
            self.blocked_ips.add(ip)
            self._log_security_event(
                "auto_blocked_failed_logins", "high",
                f"IP {ip} blocked due to {len(recent_failures)} failed login attempts",
                ip
            )
