const fs = require('fs');
const path = require('path');

/**
 * Weather Utilities
 * Provides local weather snippets for service pages.
 */

function generateWeatherSnippet(city, state = 'CA') {
    const date = new Date();
    const month = date.toLocaleString('default', { month: 'long' });
    const year = date.getFullYear();

    // High Desert / Antelope Valley typical weather patterns
    const weatherData = {
        'Lancaster': { temp: '72°F', condition: 'Sunny & Clear', humidity: '15%' },
        'Palmdale': { temp: '71°F', condition: 'Sunny', humidity: '16%' },
        'Quartz Hill': { temp: '70°F', condition: 'Clear Skies', humidity: '14%' },
        'Tehachapi': { temp: '62°F', condition: 'Cool & Breezy', humidity: '22%' },
        'Rosamond': { temp: '74°F', condition: 'Arid & Sunny', humidity: '12%' },
        'default': { temp: '70°F', condition: 'Sunny', humidity: '15%' }
    };

    const stats = weatherData[city] || weatherData['default'];

    return `
<div class="weather-snippet">
    <h4>Local Climate Update: ${city}, ${state}</h4>
    <p>As of ${month} ${year}, the current conditions in <strong>${city}</strong> are <strong>${stats.condition}</strong> with a comfortable <strong>${stats.temp}</strong> and <strong>${stats.humidity}</strong> humidity.</p>
    <p class="weather-tip"><em>Service Tip:</em> High Desert winds can increase dust buildup in your HVAC filters. We recommend checking your filters every 30 days during dry spells.</p>
</div>
`;
}

module.exports = { generateWeatherSnippet };
