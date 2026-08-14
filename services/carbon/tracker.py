import json
import os
from typing import Dict, Any, Optional
from datetime import datetime


class CarbonTracker:
    """Track cumulative carbon footprint across all trips."""
    
    def __init__(self, storage_file: str = "data/carbon_tracking.json"):
        """Initialize carbon tracker with persistent storage."""
        self.storage_file = storage_file
        self._ensure_storage_dir()
        self.data = self._load_data()
    
    def _ensure_storage_dir(self):
        """Ensure the storage directory exists."""
        os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
    
    def _load_data(self) -> Dict[str, Any]:
        """Load carbon tracking data from file."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "total_carbon_kg": 0.0,
            "total_trips": 0,
            "trips": [],
            "last_reset": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat()
        }
    
    def _save_data(self):
        """Save carbon tracking data to file."""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving carbon data: {e}")
    
    def add_trip(self, carbon_kg: float, trip_details: Optional[Dict[str, Any]] = None):
        """Add a new trip's carbon footprint."""
        self.data["total_carbon_kg"] += carbon_kg
        self.data["total_trips"] += 1
        
        trip_entry = {
            "carbon_kg": carbon_kg,
            "timestamp": datetime.now().isoformat(),
            "details": trip_details or {}
        }
        
        self.data["trips"].append(trip_entry)
        self._save_data()
    
    def get_total_carbon(self) -> float:
        """Get total cumulative carbon footprint."""
        return self.data["total_carbon_kg"]
    
    def get_total_trips(self) -> int:
        """Get total number of trips tracked."""
        return self.data["total_trips"]
    
    def get_average_carbon(self) -> float:
        """Get average carbon per trip."""
        if self.data["total_trips"] == 0:
            return 0.0
        return self.data["total_carbon_kg"] / self.data["total_trips"]
    
    def get_recent_trips(self, limit: int = 10) -> list:
        """Get recent trips."""
        return self.data["trips"][-limit:]
    
    def reset(self):
        """Reset all carbon tracking data."""
        self.data = {
            "total_carbon_kg": 0.0,
            "total_trips": 0,
            "trips": [],
            "last_reset": datetime.now().isoformat(),
            "created_at": self.data.get("created_at", datetime.now().isoformat())
        }
        self._save_data()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        return {
            "total_carbon_kg": self.data["total_carbon_kg"],
            "total_trips": self.data["total_trips"],
            "average_carbon_kg": self.get_average_carbon(),
            "last_reset": self.data.get("last_reset"),
            "created_at": self.data.get("created_at"),
            "recent_trips": self.get_recent_trips(5)
        }


carbon_tracker = CarbonTracker()
