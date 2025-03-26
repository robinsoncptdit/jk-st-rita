from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from flask import current_app
import time
import json
import os
from typing import List, Dict, Optional

class GeocodingService:
    def __init__(self):
        self.provider = current_app.config['GEOCODING_PROVIDER']
        self.api_key = current_app.config['GEOCODING_API_KEY']
        self.cache_file = os.path.join(current_app.config['UPLOAD_FOLDER'], 'geocoding_cache.json')
        self.cache = self._load_cache()
        
    def _load_cache(self) -> Dict:
        """Load geocoding cache from file."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def _save_cache(self):
        """Save geocoding cache to file."""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f)
    
    def geocode_address(self, address: str) -> Optional[Dict]:
        """Geocode a single address with caching."""
        # Check cache first
        if address in self.cache:
            return self.cache[address]
        
        try:
            if self.provider == 'nominatim':
                geolocator = Nominatim(user_agent="housing_analysis_app")
                location = geolocator.geocode(address)
                if location:
                    result = {
                        'address': address,
                        'lat': location.latitude,
                        'lng': location.longitude,
                        'provider': 'nominatim'
                    }
                    self.cache[address] = result
                    self._save_cache()
                    return result
            # Add support for other providers here (Google, Mapbox)
            
            return None
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            print(f"Geocoding error for {address}: {str(e)}")
            return None
    
    def geocode_batch(self, addresses: List[str], batch_size: int = 50) -> Dict:
        """Geocode a batch of addresses with rate limiting."""
        results = {
            'successful': [],
            'failed': [],
            'total': len(addresses)
        }
        
        for i in range(0, len(addresses), batch_size):
            batch = addresses[i:i + batch_size]
            
            for address in batch:
                result = self.geocode_address(address)
                if result:
                    results['successful'].append(result)
                else:
                    results['failed'].append(address)
            
            # Rate limiting for Nominatim
            if self.provider == 'nominatim':
                time.sleep(1)
        
        results['success_rate'] = len(results['successful']) / len(addresses)
        return results
    
    def validate_address(self, address: str) -> bool:
        """Validate if an address is complete and valid."""
        # Basic validation rules
        if not address or len(address.strip()) < 10:
            return False
        
        # Check for common invalid patterns
        invalid_patterns = [
            'P.O. Box',
            'PO Box',
            'POB',
            'Post Office Box'
        ]
        
        return not any(pattern.lower() in address.lower() for pattern in invalid_patterns) 