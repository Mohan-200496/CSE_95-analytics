"""
Advanced Security Firewall Middleware
Comprehensive protection against common attacks
"""

from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
import re
import ipaddress
from typing import Dict, Set, List, Optional
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)

class SecurityFirewall(BaseHTTPMiddleware):
    """Advanced security firewall with multiple protection layers"""
    
    def __init__(self, app):
        super().__init__(app)
        
        # Rate limiting storage
        self.rate_limits: Dict[str, List[float]] = {}
        self.blocked_ips: Dict[str, float] = {}
        
        # Security rules
        self.max_requests_per_minute = 60
        self.max_requests_per_hour = 1000
        self.block_duration = 3600  # 1 hour
        
        # Suspicious patterns
        self.malicious_patterns = [
            r'(?i)(union|select|insert|update|delete|drop|create|alter)\s+',
            r'(?i)(<script|javascript:|vbscript:|onload=|onerror=)',
            r'(?i)(\.\.[\\/]|\.\.[\\\\])',
            r'(?i)(eval\(|exec\(|system\(|shell_exec)',
            r'(?i)(base64_decode|file_get_contents|fopen)',
        ]
        
        # Allowed domains for production
        self.allowed_domains = [
            'punjab-rozgar-portal1.onrender.com',
            'punjab-rozgar-api.onrender.com', 
            'localhost',
            '127.0.0.1',
            'punjabrozgar.gov.in',
            'www.punjabrozgar.gov.in'
        ]
        
        # Security headers
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https: blob:; connect-src 'self' https://punjab-rozgar-api.onrender.com;",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "Cache-Control": "no-cache, no-store, must-revalidate, private",
            "Pragma": "no-cache",
            "Expires": "0",
            "X-Robots-Tag": "noindex, nofollow"
        }
    
    def get_client_ip(self, request: Request) -> str:
        """Get real client IP considering proxies"""
        # Check X-Forwarded-For header (for reverse proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"
    
    def is_ip_blocked(self, client_ip: str) -> bool:
        """Check if IP is temporarily blocked"""
        if client_ip in self.blocked_ips:
            if time.time() - self.blocked_ips[client_ip] > self.block_duration:
                del self.blocked_ips[client_ip]
                return False
            return True
        return False
    
    def check_rate_limit(self, client_ip: str) -> bool:
        """Advanced rate limiting with escalating blocks"""
        current_time = time.time()
        
        # Initialize if not exists
        if client_ip not in self.rate_limits:
            self.rate_limits[client_ip] = []
        
        # Clean old entries (older than 1 hour)
        self.rate_limits[client_ip] = [
            timestamp for timestamp in self.rate_limits[client_ip]
            if current_time - timestamp < 3600
        ]
        
        # Check minute limit
        minute_requests = sum(
            1 for timestamp in self.rate_limits[client_ip]
            if current_time - timestamp < 60
        )
        
        # Check hour limit
        hour_requests = len(self.rate_limits[client_ip])
        
        # Block if limits exceeded
        if minute_requests >= self.max_requests_per_minute:
            self.blocked_ips[client_ip] = current_time
            logger.warning(f"IP {client_ip} blocked for exceeding minute limit: {minute_requests} requests")
            return False
        
        if hour_requests >= self.max_requests_per_hour:
            self.blocked_ips[client_ip] = current_time
            logger.warning(f"IP {client_ip} blocked for exceeding hour limit: {hour_requests} requests")
            return False
        
        # Add current request
        self.rate_limits[client_ip].append(current_time)
        return True
    
    def check_malicious_patterns(self, request: Request) -> bool:
        """Check for malicious patterns in request"""
        # Check URL path
        for pattern in self.malicious_patterns:
            if re.search(pattern, str(request.url)):
                logger.warning(f"Malicious pattern detected in URL: {request.url}")
                return True
        
        # Check headers
        for header_name, header_value in request.headers.items():
            for pattern in self.malicious_patterns:
                if re.search(pattern, f"{header_name}: {header_value}"):
                    logger.warning(f"Malicious pattern detected in header {header_name}")
                    return True
        
        return False
    
    def validate_origin(self, request: Request) -> bool:
        """Validate request origin"""
        origin = request.headers.get("origin")
        host = request.headers.get("host")
        
        # Allow requests without origin (direct API calls)
        if not origin:
            return True
        
        # Extract domain from origin
        try:
            origin_domain = origin.replace("https://", "").replace("http://", "")
            return any(domain in origin_domain for domain in self.allowed_domains)
        except Exception:
            return False
    
    def check_request_size(self, request: Request) -> bool:
        """Check request size limits"""
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                # Limit to 50MB
                if size > 50 * 1024 * 1024:
                    logger.warning(f"Large request detected: {size} bytes")
                    return False
            except ValueError:
                pass
        return True
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_ip = self.get_client_ip(request)
        
        # Skip security for health checks and docs with relaxed CSP
        if request.url.path in ["/health", "/api/docs", "/api/redoc", "/api/openapi.json"]:
            response = await call_next(request)
            # Add relaxed CSP for docs to allow external resources
            if request.url.path in ["/api/docs", "/api/redoc"]:
                response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data: https: blob:; connect-src 'self';"
        else:
            try:
                # 1. Check if IP is blocked
                if self.is_ip_blocked(client_ip):
                    logger.warning(f"Blocked IP attempted access: {client_ip}")
                    raise HTTPException(status_code=429, detail="IP temporarily blocked")
                
                # 2. Rate limiting
                if not self.check_rate_limit(client_ip):
                    raise HTTPException(status_code=429, detail="Rate limit exceeded")
                
                # 3. Check malicious patterns
                if self.check_malicious_patterns(request):
                    self.blocked_ips[client_ip] = time.time()
                    raise HTTPException(status_code=400, detail="Malicious request detected")
                
                # 4. Validate origin
                if not self.validate_origin(request):
                    logger.warning(f"Invalid origin: {request.headers.get('origin')} from IP {client_ip}")
                    raise HTTPException(status_code=403, detail="Invalid origin")
                
                # 5. Check request size
                if not self.check_request_size(request):
                    raise HTTPException(status_code=413, detail="Request too large")
                
                # Process request
                response = await call_next(request)
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Security firewall error: {e}")
                raise HTTPException(status_code=500, detail="Security check failed")
        
        # Add security headers
        for header_name, header_value in self.security_headers.items():
            response.headers[header_name] = header_value
        
        # Add processing time header
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response