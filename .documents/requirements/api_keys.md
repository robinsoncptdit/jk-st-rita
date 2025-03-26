# Required API Keys for Housing & Income Analysis Tool

## Current Requirements

For the basic functionality of the application, no API keys are required as we're using the free Nominatim geocoding service by default. However, for production use or higher request volumes, you might want to consider using one of the following alternative geocoding services:

### Optional Geocoding Services

1. **Google Maps Geocoding API**
   - Sign up at: https://console.cloud.google.com/
   - Enable the Geocoding API in your project
   - Create credentials to get your API key
   - Set in `.env` file as: `GEOCODING_PROVIDER=google` and `GEOCODING_API_KEY=your_api_key`
   - Note: This is a paid service with a free tier

2. **Mapbox**
   - Sign up at: https://www.mapbox.com/
   - Get your access token from your account dashboard
   - Set in `.env` file as: `GEOCODING_PROVIDER=mapbox` and `GEOCODING_API_KEY=your_access_token`
   - Note: This is a paid service with a free tier

## Default Configuration

By default, the application uses:
- **Nominatim** for geocoding (free, no API key required)
  - Has usage limits of 1 request per second
  - Suitable for development and testing
  - For production use, consider switching to a paid service

## Setting Up API Keys

1. Create a `.env` file in the root directory of the project
2. Add your chosen API keys in the following format:
```
GEOCODING_PROVIDER=nominatim  # or 'google' or 'mapbox'
GEOCODING_API_KEY=your_api_key_here  # only needed for google or mapbox
```

## Usage Considerations

- **Development**: The default Nominatim service is sufficient
- **Production**: Consider using Google Maps or Mapbox for:
  - Higher request limits
  - Better reliability
  - Additional features
  - Commercial use compliance 