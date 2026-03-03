/**
 * Utility for generating a client-side live weather component.
 * Uses Open-Meteo for free, no-key real-time weather data.
 */

function generateWeatherSnippet(city, state) {
    const location = `${city}, ${state}`;
    return `
<div class="live-weather-section" style="margin: 30px 0; padding: 25px; border: 1px solid #e0e0e0; border-radius: 12px; background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%); box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h2 style="margin: 0; font-size: 1.5rem; color: #333;">Live Weather in ${city}</h2>
        <div id="weather-status" style="font-size: 0.9rem; color: #1a73e8; font-weight: bold; background: #e8f0fe; padding: 4px 12px; border-radius: 20px;">Updating...</div>
    </div>
    
    <div id="weather-display" style="display: flex; gap: 40px; align-items: center; min-height: 80px;">
        <div style="text-align: center;">
            <div id="weather-temp" style="font-size: 3rem; font-weight: bold; color: #1a73e8;">--°F</div>
            <div id="weather-desc" style="font-size: 1rem; color: #666; text-transform: capitalize;">Checking conditions...</div>
        </div>
        
        <div style="flex-grow: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
            <div style="background: #fff; padding: 12px; border-radius: 8px; border: 1px solid #f0f0f0;">
                <span style="display: block; font-size: 0.8rem; color: #999; margin-bottom: 4px;">Humidity</span>
                <span id="weather-humidity" style="font-weight: bold; color: #333;">--%</span>
            </div>
            <div style="background: #fff; padding: 12px; border-radius: 8px; border: 1px solid #f0f0f0;">
                <span style="display: block; font-size: 0.8rem; color: #999; margin-bottom: 4px;">Wind Speed</span>
                <span id="weather-wind" style="font-weight: bold; color: #333;">-- mph</span>
            </div>
        </div>
    </div>

    <script>
    (function() {
        async function fetchWeather() {
            try {
                // Heuristic: Lancaster, CA coords for demo or lookup via city/state
                const city = "${city}";
                let lat = 34.6868, lon = -118.1542; // Default Lancaster
                
                if (city.includes("Palmdale")) { lat = 34.5794; lon = -118.1165; }
                if (city.includes("Quartz Hill")) { lat = 34.6469; lon = -118.2120; }

                const response = await fetch(\`https://api.open-meteo.com/v1/forecast?latitude=\${lat}&longitude=\${lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m&temperature_unit=fahrenheit&wind_speed_unit=mph\`);
                const data = await response.json();
                
                const temp = Math.round(data.current.temperature_2m);
                const humidity = data.current.relative_humidity_2m;
                const wind = Math.round(data.current.wind_speed_10m);
                
                document.getElementById('weather-temp').innerText = temp + '°F';
                document.getElementById('weather-humidity').innerText = humidity + '%';
                document.getElementById('weather-wind').innerText = wind + ' mph';
                document.getElementById('weather-status').innerText = 'Live';
                
                // Simplified weather code to text
                const codes = { 0: 'Clear sky', 1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast', 45: 'Fog', 48: 'Depositing rime fog', 51: 'Light drizzle', 61: 'Slight rain', 71: 'Slight snow', 95: 'Thunderstorm' };
                document.getElementById('weather-desc').innerText = codes[data.current.weather_code] || 'Clear conditions';
                
            } catch (err) {
                console.error('Weather fetch error:', err);
                document.getElementById('weather-status').innerText = 'Offline';
            }
        }
        fetchWeather();
    })();
    </script>
</div>
`;
}

module.exports = {
    generateWeatherSnippet
};
