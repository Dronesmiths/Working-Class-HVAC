/**
 * Utility for generating a client-side live weather component.
 * Uses Open-Meteo for core weather and Google APIs for Air Quality/Pollen.
 */

function generateWeatherSnippet(city, state, apiKey = "") {
    const location = `${city}, ${state}`;
    return `
<div class="live-weather-section" style="margin: 30px 0; padding: 25px; border: 1px solid #e0e0e0; border-radius: 12px; background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%); box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h2 style="margin: 0; font-size: 1.5rem; color: #333;">Local Environment: ${city}</h2>
        <div id="weather-status" style="font-size: 0.9rem; color: #1a73e8; font-weight: bold; background: #e8f0fe; padding: 4px 12px; border-radius: 20px;">Live Data</div>
    </div>
    
    <div id="weather-display" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; align-items: center;">
        <div style="text-align: center; border-right: 1px solid #eee; padding-right: 20px;">
            <div id="weather-temp" style="font-size: 2.5rem; font-weight: bold; color: #1a73e8;">--°F</div>
            <div id="weather-desc" style="font-size: 0.9rem; color: #666; text-transform: capitalize;">Checking...</div>
        </div>
        
        <div style="background: #fff; padding: 12px; border-radius: 8px; border: 1px solid #f0f0f0; text-align: center;">
            <span style="display: block; font-size: 0.75rem; color: #999; margin-bottom: 4px; text-transform: uppercase;">Air Quality</span>
            <span id="weather-aqi" style="font-weight: bold; color: #2ecc71;">Excellent</span>
            <div id="aqi-val" style="font-size: 0.7rem; color: #aaa;">AQI: --</div>
        </div>

        <div style="background: #fff; padding: 12px; border-radius: 8px; border: 1px solid #f0f0f0; text-align: center;">
            <span style="display: block; font-size: 0.75rem; color: #999; margin-bottom: 4px; text-transform: uppercase;">Pollen Risk</span>
            <span id="pollen-status" style="font-weight: bold; color: #f1c40f;">Moderate</span>
        </div>

        <div style="background: #fff; padding: 12px; border-radius: 8px; border: 1px solid #f0f0f0; text-align: center;">
            <span style="display: block; font-size: 0.75rem; color: #999; margin-bottom: 4px; text-transform: uppercase;">Humidity</span>
            <span id="weather-humidity" style="font-weight: bold; color: #333;">--%</span>
        </div>
    </div>

    <script>
    (function() {
        const API_KEY = "${apiKey}";
        const lat = ${city.includes("Palmdale") ? 34.5794 : (city.includes("Quartz Hill") ? 34.6469 : 34.6868)};
        const lon = ${city.includes("Palmdale") ? -118.1165 : (city.includes("Quartz Hill") ? -118.2120 : -118.1542)};

        async function fetchWeather() {
            try {
                const response = await fetch(\`https://api.open-meteo.com/v1/forecast?latitude=\${lat}&longitude=\${lon}&current=temperature_2m,relative_humidity_2m,weather_code&temperature_unit=fahrenheit\`);
                const data = await response.json();
                document.getElementById('weather-temp').innerText = Math.round(data.current.temperature_2m) + '°F';
                if (document.getElementById('test-temp')) document.getElementById('test-temp').innerText = Math.round(data.current.temperature_2m) + '°F';
                document.getElementById('weather-humidity').innerText = data.current.relative_humidity_2m + '%';
                const codes = { 0: 'Clear sky', 1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast' };
                document.getElementById('weather-desc').innerText = codes[data.current.weather_code] || 'Clear';
            } catch (e) {}
        }

        async function fetchAirHealth() {
            if (!API_KEY) return;
            try {
                // Fetch AQI
                const aqiRes = await fetch(\`https://airquality.googleapis.com/v1/currentConditions:lookup?key=\${API_KEY}\`, {
                    method: 'POST', body: JSON.stringify({ location: { latitude: lat, longitude: lon } })
                });
                const aqiData = await aqiRes.json();
                if (aqiData.indexes) {
                    const idx = aqiData.indexes[0];
                    document.getElementById('weather-aqi').innerText = idx.category;
                    if (document.getElementById('test-aqi')) document.getElementById('test-aqi').innerText = idx.category;
                    document.getElementById('aqi-val').innerText = 'Index: ' + idx.aqi;
                    document.getElementById('weather-aqi').style.color = idx.color && idx.color.red ? 'rgb('+(idx.color.red*255)+','+(idx.color.green*255)+','+(idx.color.blue*255)+')' : '#2ecc71';
                }

                // Fetch Pollen
                const pollenRes = await fetch(\`https://pollen.googleapis.com/v1/forecast:lookup?key=\${API_KEY}&location.latitude=\${lat}&location.longitude=\${lon}&days=1\`);
                const pollenData = await pollenRes.json();
                if (pollenData.dailyInfo && pollenData.dailyInfo[0].pollenTypeInfo) {
                    const info = pollenData.dailyInfo[0].pollenTypeInfo[0];
                    document.getElementById('pollen-status').innerText = info.indexInfo.category;
                    if (document.getElementById('test-pollen')) document.getElementById('test-pollen').innerText = info.indexInfo.category;
                }
            } catch (e) {
                console.warn('Air/Pollen API limited or error', e);
            }
        }

        fetchWeather();
        fetchAirHealth();
    })();
    </script>
</div>
`;
}

module.exports = {
    generateWeatherSnippet
};
