"""
API Security Monitoring and Analytics Module
Provides real-time security monitoring and threat intelligence
for the Punjab Rozgar Portal
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

@dataclass
class SecurityEvent:
    """Security event data structure"""
    timestamp: str
    event_type: str
    severity: str
    description: str
    ip_address: str
    user_id: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    threat_level: int = 0
    country: Optional[str] = None
    user_agent: Optional[str] = None

@dataclass
class ThreatIntelligence:
    """Threat intelligence data"""
    ip_address: str
    threat_score: int
    last_activity: str
    threat_types: List[str]
    blocked: bool
    first_seen: str
    request_count: int

@dataclass
class SecurityMetrics:
    """Security metrics aggregation"""
    total_requests: int
    blocked_requests: int
    threat_level_counts: Dict[str, int]
    top_threats: List[str]
    geographic_distribution: Dict[str, int]
    hourly_stats: Dict[str, int]

class SecurityMonitor:
    """Real-time security monitoring and analytics"""
    
    def __init__(self, retention_days: int = 30):
        self.retention_days = retention_days
        
        # Event storage
        self.security_events = deque()
        self.threat_intelligence = defaultdict(lambda: {
            'threat_score': 0,
            'last_activity': datetime.utcnow().isoformat(),
            'threat_types': [],
            'blocked': False,
            'first_seen': datetime.utcnow().isoformat(),
            'request_count': 0
        })
        
        # Metrics aggregation
        self.hourly_stats = defaultdict(int)
        self.daily_stats = defaultdict(int)
        self.threat_level_counts = defaultdict(int)
        
        # Geographic tracking
        self.geographic_stats = defaultdict(int)
        
        # Pattern recognition
        self.attack_patterns = defaultdict(list)
        
        # Known threat indicators
        self.known_bad_ips = set()
        self.suspicious_user_agents = [
            'sqlmap', 'nmap', 'burp', 'nikto', 'dirb', 'gobuster',
            'metasploit', 'havij', 'sqlninja', 'w3af'
        ]
        
        # Initialize cleanup timer
        self.last_cleanup = time.time()
        
        # Load threat intelligence feeds
        self._load_threat_feeds()
    
    def _load_threat_feeds(self):
        """Load external threat intelligence feeds"""
        # This would integrate with external threat feeds in production
        # For now, we'll use a basic list of known malicious IPs
        known_threats = [
            '192.168.1.100',  # Example threat IP
            '10.0.0.5',       # Example internal threat
        ]
        self.known_bad_ips.update(known_threats)
    
    def record_security_event(self, event: SecurityEvent):
        """Record a security event for monitoring"""
        # Add to event log
        self.security_events.append(event)
        
        # Update threat intelligence
        self._update_threat_intelligence(event)
        
        # Update metrics
        self._update_metrics(event)
        
        # Check for attack patterns
        self._analyze_patterns(event)
        
        # Cleanup old data periodically
        if time.time() - self.last_cleanup > 3600:  # Every hour
            self._cleanup_old_data()
            self.last_cleanup = time.time()
    
    def _update_threat_intelligence(self, event: SecurityEvent):
        """Update threat intelligence for IP"""
        ip = event.ip_address
        intel = self.threat_intelligence[ip]
        
        # Update activity timestamp
        intel['last_activity'] = event.timestamp
        
        # Increment request count
        intel['request_count'] += 1
        
        # Update threat score based on event
        score_increases = {
            'sql_injection': 25,
            'xss_attempt': 20,
            'command_injection': 30,
            'brute_force': 15,
            'rate_limit_exceeded': 5,
            'suspicious_activity': 10
        }
        
        score_increase = score_increases.get(event.event_type, 5)
        intel['threat_score'] += score_increase
        
        # Add threat type if not already present
        if event.event_type not in intel['threat_types']:
            intel['threat_types'].append(event.event_type)
        
        # Auto-block high-threat IPs
        if intel['threat_score'] > 100:
            intel['blocked'] = True
            self.known_bad_ips.add(ip)
        
        # Update geographic info if available
        if event.country:
            self.geographic_stats[event.country] += 1
    
    def _update_metrics(self, event: SecurityEvent):
        """Update security metrics"""
        # Hourly stats
        hour_key = datetime.fromisoformat(event.timestamp.replace('Z', '+00:00')).strftime('%Y-%m-%d-%H')
        self.hourly_stats[hour_key] += 1
        
        # Daily stats
        day_key = datetime.fromisoformat(event.timestamp.replace('Z', '+00:00')).strftime('%Y-%m-%d')
        self.daily_stats[day_key] += 1
        
        # Threat level counts
        self.threat_level_counts[event.severity] += 1
    
    def _analyze_patterns(self, event: SecurityEvent):
        """Analyze attack patterns for correlation"""
        # Store recent events for pattern analysis
        self.attack_patterns[event.ip_address].append({
            'timestamp': event.timestamp,
            'event_type': event.event_type,
            'endpoint': event.endpoint
        })
        
        # Keep only recent events (last hour)
        cutoff = datetime.utcnow() - timedelta(hours=1)
        self.attack_patterns[event.ip_address] = [
            e for e in self.attack_patterns[event.ip_address]
            if datetime.fromisoformat(e['timestamp'].replace('Z', '+00:00')) > cutoff
        ]
    
    def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        cutoff = datetime.utcnow() - timedelta(days=self.retention_days)
        
        # Clean old events
        self.security_events = deque([
            event for event in self.security_events
            if datetime.fromisoformat(event.timestamp.replace('Z', '+00:00')) > cutoff
        ])
        
        # Clean old threat intelligence for inactive IPs
        inactive_cutoff = datetime.utcnow() - timedelta(days=7)
        for ip in list(self.threat_intelligence.keys()):
            last_activity = datetime.fromisoformat(
                self.threat_intelligence[ip]['last_activity'].replace('Z', '+00:00')
            )
            if last_activity < inactive_cutoff and not self.threat_intelligence[ip]['blocked']:
                del self.threat_intelligence[ip]
        
        # Clean old attack patterns
        for ip in list(self.attack_patterns.keys()):
            if not self.attack_patterns[ip]:
                del self.attack_patterns[ip]
    
    def get_security_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive security dashboard data"""
        now = datetime.utcnow()
        
        # Calculate metrics for different time periods
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        # Recent events
        recent_events = [
            asdict(event) for event in self.security_events
            if datetime.fromisoformat(event.timestamp.replace('Z', '+00:00')) > last_24h
        ]
        
        # Threat summary
        threats_24h = len(recent_events)
        active_threats = sum(1 for intel in self.threat_intelligence.values() if intel['threat_score'] > 50)
        blocked_ips = sum(1 for intel in self.threat_intelligence.values() if intel['blocked'])
        
        # Top threat countries
        top_countries = sorted(self.geographic_stats.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Top threat types
        event_types = defaultdict(int)
        for event in recent_events:
            event_types[event['event_type']] += 1
        top_threat_types = sorted(event_types.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Hourly activity for last 24 hours
        hourly_activity = {}
        for i in range(24):
            hour_time = now - timedelta(hours=i)
            hour_key = hour_time.strftime('%Y-%m-%d-%H')
            hourly_activity[hour_time.strftime('%H:00')] = self.hourly_stats.get(hour_key, 0)
        
        return {
            'summary': {
                'total_events_24h': threats_24h,
                'active_threats': active_threats,
                'blocked_ips': blocked_ips,
                'threat_score_avg': sum(intel['threat_score'] for intel in self.threat_intelligence.values()) / max(len(self.threat_intelligence), 1)
            },
            'recent_events': recent_events[-50:],  # Last 50 events
            'threat_intelligence': [
                {
                    'ip_address': ip,
                    'threat_score': intel['threat_score'],
                    'threat_types': intel['threat_types'],
                    'last_activity': intel['last_activity'],
                    'request_count': intel['request_count'],
                    'blocked': intel['blocked']
                }
                for ip, intel in sorted(
                    self.threat_intelligence.items(),
                    key=lambda x: x[1]['threat_score'],
                    reverse=True
                )[:20]  # Top 20 threats
            ],
            'geographic_distribution': dict(top_countries),
            'top_threat_types': dict(top_threat_types),
            'hourly_activity': hourly_activity,
            'severity_breakdown': dict(self.threat_level_counts)
        }
    
    def get_ip_intelligence(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Get detailed threat intelligence for specific IP"""
        if ip_address not in self.threat_intelligence:
            return None
        
        intel = self.threat_intelligence[ip_address]
        
        # Get recent events for this IP
        recent_events = [
            asdict(event) for event in self.security_events
            if event.ip_address == ip_address
        ][-20:]  # Last 20 events
        
        # Get attack patterns
        patterns = self.attack_patterns.get(ip_address, [])
        
        return {
            'ip_address': ip_address,
            'threat_intelligence': intel,
            'recent_events': recent_events,
            'attack_patterns': patterns,
            'is_known_threat': ip_address in self.known_bad_ips
        }
    
    def block_ip(self, ip_address: str, reason: str = "Manual block"):
        """Manually block an IP address"""
        self.threat_intelligence[ip_address]['blocked'] = True
        self.known_bad_ips.add(ip_address)
        
        # Record the block event
        event = SecurityEvent(
            timestamp=datetime.utcnow().isoformat() + 'Z',
            event_type='manual_block',
            severity='high',
            description=f"IP manually blocked: {reason}",
            ip_address=ip_address
        )
        self.record_security_event(event)
    
    def unblock_ip(self, ip_address: str):
        """Unblock an IP address"""
        if ip_address in self.threat_intelligence:
            self.threat_intelligence[ip_address]['blocked'] = False
        self.known_bad_ips.discard(ip_address)
        
        # Record the unblock event
        event = SecurityEvent(
            timestamp=datetime.utcnow().isoformat() + 'Z',
            event_type='manual_unblock',
            severity='medium',
            description="IP manually unblocked",
            ip_address=ip_address
        )
        self.record_security_event(event)
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is blocked"""
        return (ip_address in self.known_bad_ips or 
                (ip_address in self.threat_intelligence and 
                 self.threat_intelligence[ip_address]['blocked']))

# Global security monitor instance
security_monitor = SecurityMonitor()