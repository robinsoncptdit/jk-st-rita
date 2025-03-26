from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from flask import current_app
import time
import json
import os
from typing import List, Dict, Optional

class GeocodingService:
    def __init__(self):
        self._provider = None
        self._cache = {}
        self._cache_file = None
        
    @property
    def provider(self):
        if self._provider is None:
            with current_app.app_context():
                provider_name = current_app.config.get('GEOCODING_PROVIDER', 'nominatim')
                if provider_name.lower() == 'nominatim':
                    self._provider = Nominatim(user_agent="housing_income_analysis")
        return self._provider
    
    @property
    def cache_file(self):
        if self._cache_file is None:
            with current_app.app_context():
                self._cache_file = os.path.join(current_app.config['UPLOAD_FOLDER'], 'geocoding_cache.json')
        return self._cache_file
    
    def _load_cache(self) -> Dict:
        """Load geocoding cache from file."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                current_app.logger.warning("Invalid cache file, starting with empty cache")
        return {}
    
    def _save_cache(self):
        """Save geocoding cache to file."""
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        with open(self.cache_file, 'w') as f:
            json.dump(self._cache, f)
    
    def geocode(self, address: str) -> Optional[Dict]:
        """Geocode an address to get its coordinates."""
        if address in self._cache:
            return self._cache[address]
        
        try:
            location = self.provider.geocode(address)
            if location:
                result = {
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'address': location.address
                }
                self._cache[address] = result
                self._save_cache()
                return result
            return None
        except GeocoderTimedOut:
            time.sleep(1)  # Wait before retrying
            return self.geocode(address)  # Retry once
        except Exception as e:
            current_app.logger.error(f"Geocoding error for address {address}: {str(e)}")
            return None

    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict]:
        """Get address from coordinates."""
        key = f"{latitude},{longitude}"
        if key in self._cache:
            return self._cache[key]
        
        try:
            location = self.provider.reverse((latitude, longitude))
            if location:
                result = {
                    'address': location.address,
                    'raw': location.raw
                }
                self._cache[key] = result
                self._save_cache()
                return result
            return None
        except GeocoderTimedOut:
            time.sleep(1)  # Wait before retrying
            return self.reverse_geocode(latitude, longitude)  # Retry once
        except Exception as e:
            current_app.logger.error(f"Reverse geocoding error for coordinates ({latitude}, {longitude}): {str(e)}")
            return None
    
    def geocode_address(self, address: str) -> Optional[Dict]:
        """Geocode a single address with caching."""
        # Check cache first
        if address in self._cache:
            return self._cache[address]
        
        try:
            location = self.geocode(address)
            if location:
                result = {
                    'address': address,
                    'lat': location['latitude'],
                    'lng': location['longitude'],
                    'provider': 'nominatim'
                }
                self._cache[address] = result
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