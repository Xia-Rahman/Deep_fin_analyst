import time
from collections import deque

class RateLimiter:
    """
    Tracks Request Per Minute (RPM) limits for different models.
    Enforces waits if limits are exceeded.
    """
    def __init__(self):
        # Stores timestamps of requests: {model_id: deque([t1, t2, ...])}
        self.request_history = {}
    
    def wait_for_slot(self, model_id: str, rpm_limit: int):
        """
        Checks if the model has available slots in the current minute window.
        If not, sleeps until a slot opens up.
        """
        if rpm_limit <= 0:
            return # No limit

        if model_id not in self.request_history:
            self.request_history[model_id] = deque()
        
        history = self.request_history[model_id]
        now = time.time()
        
        # 1. Clean up requests older than 60 seconds
        while history and history[0] < now - 60:
            history.popleft()
            
        # 2. Check if we are at capacity
        if len(history) >= rpm_limit:
            # We hit the limit. Wait until the oldest request falls out of the 60s window.
            oldest_request_time = history[0]
            wait_time = 60 - (now - oldest_request_time) + 0.5 # Add small buffer
            
            if wait_time > 0:
                print(f"⏳ Rate Limit ({rpm_limit} RPM) hit for {model_id}. Waiting {wait_time:.1f}s...")
                time.sleep(wait_time)
                
                # After waiting, re-fetch time and clean up to ensure state is correct
                now = time.time()
                while history and history[0] < now - 60:
                    history.popleft()
        
        # 3. Record this request
        self.request_history[model_id].append(time.time())

# Global singleton instance
GLOBAL_RATE_LIMITER = RateLimiter()
