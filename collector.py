"""Data collector module for fetching sensor data from The Things Network API"""
import json
import requests
from typing import List, Dict, Optional
from datetime import datetime
import config
from database import SensorDatabase


class SensorDataCollector:
    """Collects sensor data from The Things Network API"""
    
    def __init__(self, api_url: str = config.API_URL, 
                 api_token: str = config.API_TOKEN,
                 database: Optional[SensorDatabase] = None):
        self.api_url = api_url
        self.api_token = api_token
        self.database = database or SensorDatabase()
    
    def fetch_data(self, lookback_hours: int = config.LOOKBACK_HOURS) -> List[Dict]:
        """
        Fetch data from The Things Network API
        
        Args:
            lookback_hours: How many hours of historical data to fetch
            
        Returns:
            List of parsed sensor readings
        """
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Accept': 'text/event-stream'
        }
        
        params = {
            'last': f'{lookback_hours}h'
        }
        
        try:
            response = requests.get(
                self.api_url,
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            # Parse the line-separated JSON messages
            readings = []
            for line in response.text.strip().split('\n'):
                if line.strip():
                    try:
                        data = json.loads(line)
                        parsed = self._parse_message(data)
                        if parsed:
                            readings.append(parsed)
                    except json.JSONDecodeError as e:
                        print(f"Error parsing line: {e}")
                        continue
            
            return readings
        except requests.HTTPError as e:
            status_code = e.response.status_code if e.response is not None else None
            if status_code in {401, 403}:
                print(
                    "Authentication/authorization failed while fetching TTN data "
                    f"(HTTP {status_code}). Verify DRAGINO_API_URL app id, token, and token rights."
                )
            print(f"Error fetching data from API: {e}")
            return []
            
        except requests.RequestException as e:
            print(f"Error fetching data from API: {e}")
            return []
    
    def _parse_message(self, message: Dict) -> Optional[Dict]:
        """Parse a single message from the API response"""
        try:
            result = message.get('result', {})
            device_ids = result.get('end_device_ids', {})
            uplink = result.get('uplink_message', {})
            decoded = uplink.get('decoded_payload', {})
            
            # Get RSSI and SNR from the first gateway metadata
            rx_metadata = uplink.get('rx_metadata', [])
            rssi = rx_metadata[0].get('rssi') if rx_metadata else None
            snr = rx_metadata[0].get('snr') if rx_metadata else None
            
            reading = {
                'device_id': device_ids.get('device_id'),
                'received_at': result.get('received_at'),
                'temp_sht': decoded.get('TempC_SHT'),
                'temp_ds': decoded.get('TempC_DS'),
                'humidity': decoded.get('Hum_SHT'),
                'battery_voltage': decoded.get('BatV'),
                'battery_status': decoded.get('Bat_status'),
                'f_cnt': uplink.get('f_cnt'),
                'rssi': rssi,
                'snr': snr,
                'raw_data': json.dumps(message)
            }
            
            # Only return if we have required fields
            if reading['device_id'] and reading['received_at']:
                return reading
                
        except Exception as e:
            print(f"Error parsing message: {e}")
        
        return None
    
    def collect_and_store(self, lookback_hours: int = config.LOOKBACK_HOURS) -> Dict:
        """
        Fetch data from API and store in database
        
        Returns:
            Dictionary with statistics about the collection
        """
        print(f"Fetching sensor data (last {lookback_hours} hours)...")
        readings = self.fetch_data(lookback_hours)
        
        if not readings:
            print("No readings fetched")
            return {
                'fetched': 0,
                'stored': 0,
                'duplicates': 0
            }
        
        print(f"Fetched {len(readings)} readings")
        
        stored = 0
        duplicates = 0
        
        for reading in readings:
            if self.database.insert_reading(reading):
                stored += 1
            else:
                duplicates += 1
        
        print(f"Stored {stored} new readings, skipped {duplicates} duplicates")
        
        return {
            'fetched': len(readings),
            'stored': stored,
            'duplicates': duplicates
        }
    
    def get_current_temperature(self, device_id: str = config.DEVICE_ID) -> Optional[Dict]:
        """Get the most recent temperature reading for a device"""
        readings = self.database.get_latest_readings(device_id=device_id, limit=1)
        return readings[0] if readings else None


if __name__ == '__main__':
    # Test the collector
    collector = SensorDataCollector()
    result = collector.collect_and_store()
    print(f"\nCollection Results: {result}")
    
    # Show latest reading
    latest = collector.get_current_temperature()
    if latest:
        print(f"\nLatest Reading:")
        print(f"  Time: {latest['received_at']}")
        print(f"  Temperature (SHT): {latest['temp_sht']}°C")
        print(f"  Humidity: {latest['humidity']}%")
        print(f"  Battery: {latest['battery_voltage']}V")
