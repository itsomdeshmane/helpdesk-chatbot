"""
Rate Limiting Middleware
Simple in-memory rate limiter with sliding window
For production, use Redis-backed rate limiting (slowapi + Redis)
"""
from typing import Dict, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import time

class RateLimiter:
    """
    In-memory rate limiter using sliding window algorithm
    Thread-safe for single-process deployments
    """
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_size: int = 10
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_size = burst_size
        
        # Store: {client_id: [(timestamp, count), ...]}
        self.requests: Dict[str, list] = defaultdict(list)
        
        # Cleanup old entries periodically
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 minutes
    
    def _cleanup_old_requests(self):
        """Remove requests older than 1 hour"""
        current_time = time.time()
        
        if current_time - self.last_cleanup > self.cleanup_interval:
            cutoff = current_time - 3600  # 1 hour ago
            
            for client_id in list(self.requests.keys()):
                self.requests[client_id] = [
                    (ts, count) for ts, count in self.requests[client_id]
                    if ts > cutoff
                ]
                
                # Remove empty entries
                if not self.requests[client_id]:
                    del self.requests[client_id]
            
            self.last_cleanup = current_time
    
    def _get_client_id(self, request: Request) -> str:
        """
        Extract client identifier from request
        Priority: User ID > API Key > IP Address
        """
        # Try to get authenticated user
        if hasattr(request.state, 'user') and request.state.user:
            return f"user:{request.state.user.get('user_id', 'unknown')}"
        
        # Try API key (if implemented)
        api_key = request.headers.get('X-API-Key')
        if api_key:
            return f"apikey:{api_key[:16]}"
        
        # Fallback to IP address
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            # Get first IP in chain (client)
            client_ip = forwarded_for.split(',')[0].strip()
        else:
            client_ip = request.client.host if request.client else 'unknown'
        
        return f"ip:{client_ip}"
    
    def is_allowed(self, request: Request) -> Tuple[bool, Dict[str, int]]:
        """
        Check if request is allowed based on rate limits
        
        Returns:
            (is_allowed, limits_info)
        """
        self._cleanup_old_requests()
        
        client_id = self._get_client_id(request)
        current_time = time.time()
        
        # Get recent requests
        recent_requests = self.requests[client_id]
        
        # Count requests in last minute
        minute_ago = current_time - 60
        requests_last_minute = sum(
            count for ts, count in recent_requests if ts > minute_ago
        )
        
        # Count requests in last hour
        hour_ago = current_time - 3600
        requests_last_hour = sum(
            count for ts, count in recent_requests if ts > hour_ago
        )
        
        # Check burst (last 10 seconds)
        burst_window = current_time - 10
        burst_requests = sum(
            count for ts, count in recent_requests if ts > burst_window
        )
        
        # Determine if request is allowed
        is_allowed = (
            requests_last_minute < self.requests_per_minute and
            requests_last_hour < self.requests_per_hour and
            burst_requests < self.burst_size
        )
        
        # Add current request if allowed
        if is_allowed:
            recent_requests.append((current_time, 1))
        
        # Return status and limits
        limits_info = {
            'requests_per_minute': self.requests_per_minute,
            'requests_last_minute': requests_last_minute,
            'requests_per_hour': self.requests_per_hour,
            'requests_last_hour': requests_last_hour,
            'burst_size': self.burst_size,
            'burst_requests': burst_requests
        }
        
        return is_allowed, limits_info
    
    async def __call__(self, request: Request, call_next):
        """
        Middleware function
        """
        # Skip rate limiting for health checks
        if request.url.path in ['/health', '/metrics', '/']:
            return await call_next(request)
        
        # Check rate limit
        is_allowed, limits = self.is_allowed(request)
        
        if not is_allowed:
            # Return 429 Too Many Requests
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please slow down.",
                    "limits": {
                        "requests_per_minute": limits['requests_per_minute'],
                        "requests_per_hour": limits['requests_per_hour']
                    },
                    "retry_after": 60  # Try again in 60 seconds
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit-Minute": str(limits['requests_per_minute']),
                    "X-RateLimit-Limit-Hour": str(limits['requests_per_hour']),
                    "X-RateLimit-Remaining-Minute": str(max(0, limits['requests_per_minute'] - limits['requests_last_minute'])),
                    "X-RateLimit-Remaining-Hour": str(max(0, limits['requests_per_hour'] - limits['requests_last_hour']))
                }
            )
        
        # Add rate limit headers to response
        response = await call_next(request)
        
        response.headers["X-RateLimit-Limit-Minute"] = str(limits['requests_per_minute'])
        response.headers["X-RateLimit-Remaining-Minute"] = str(max(0, limits['requests_per_minute'] - limits['requests_last_minute'] - 1))
        response.headers["X-RateLimit-Limit-Hour"] = str(limits['requests_per_hour'])
        response.headers["X-RateLimit-Remaining-Hour"] = str(max(0, limits['requests_per_hour'] - limits['requests_last_hour'] - 1))
        
        return response


# Global rate limiter instance (configure via environment variables)
import os

# Different limits for different environments
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    # Stricter limits in production
    rate_limiter = RateLimiter(
        requests_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "30")),
        requests_per_hour=int(os.getenv("RATE_LIMIT_PER_HOUR", "500")),
        burst_size=int(os.getenv("RATE_LIMIT_BURST", "5"))
    )
else:
    # More lenient in development
    rate_limiter = RateLimiter(
        requests_per_minute=100,
        requests_per_hour=2000,
        burst_size=20
    )

print(f"⏱️  Rate limiting configured ({ENVIRONMENT}): "
      f"{rate_limiter.requests_per_minute}/min, "
      f"{rate_limiter.requests_per_hour}/hour, "
      f"burst={rate_limiter.burst_size}")

