const maps = require('./map-utils');

/**
 * Utility for enriching HVAC articles with local data, stats, and maps.
 */

async function getEnrichedContent(title, pillar, location = "Lancaster, CA", mapsApiConfig = {}) {
    console.log(`[AI-Enrich] Generating high-quality content for: ${title}`);

    const { apiKey, placeId, flags, businessAddress } = mapsApiConfig;

    // ... (statsHtml and tableHtml remain same)

    // 1. Data-Driven Stat Block (Stubbed with representative HVAC data for Lancaster)
    const statsHtml = `
<div class="stat-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0;">
    <div class="stat-card" style="padding: 24px; border: 1px solid #eee; border-radius: 12px; text-align: center; background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <h3 style="font-size: 2rem; color: #1a73e8; margin-bottom: 8px;">100°F+</h3>
        <p style="margin: 0; color: #555;">Average Lancaster Summer Peaks</p>
    </div>
    <div class="stat-card" style="padding: 24px; border: 1px solid #eee; border-radius: 12px; text-align: center; background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <h3 style="font-size: 2rem; color: #1a73e8; margin-bottom: 8px;">20-30%</h3>
        <p style="margin: 0; color: #555;">Efficiency Gain with Spring Prep</p>
    </div>
    <div class="stat-card" style="padding: 24px; border: 1px solid #eee; border-radius: 12px; text-align: center; background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <h3 style="font-size: 2rem; color: #1a73e8; margin-bottom: 8px;">15-20 yrs</h3>
        <p style="margin: 0; color: #555;">Expected Life of Maintained Systems</p>
    </div>
</div>
`;

    // 2. Data Table for Comparison
    const tableHtml = `
<div class="data-table-container" style="margin: 30px 0;">
    <h3 style="margin-bottom: 15px;">Lancaster HVAC Maintenance Checklist</h3>
    <table style="width: 100%; border-collapse: collapse; font-family: sans-serif;">
        <thead>
            <tr style="background-color: #f4f4f4; border-bottom: 2px solid #eee;">
                <th style="padding: 12px; text-align: left; border: 1px solid #eee;">Service Task</th>
                <th style="padding: 12px; text-align: left; border: 1px solid #eee;">Frequency</th>
                <th style="padding: 12px; text-align: left; border: 1px solid #eee;">Benefit</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="padding: 12px; border: 1px solid #eee;">Filter Replacement</td>
                <td style="padding: 12px; border: 1px solid #eee;">Every 3 Months</td>
                <td style="padding: 12px; border: 1px solid #eee;">Improved Air Quality</td>
            </tr>
            <tr>
                <td style="padding: 12px; border: 1px solid #eee;">Coil Cleaning</td>
                <td style="padding: 12px; border: 1px solid #eee;">Annually (Spring)</td>
                <td style="padding: 12px; border: 1px solid #eee;">Lower Utility Bills</td>
            </tr>
            <tr>
                <td style="padding: 12px; border: 1px solid #eee;">Refrigerant Check</td>
                <td style="padding: 12px; border: 1px solid #eee;">Pre-Summer</td>
                <td style="padding: 12px; border: 1px solid #eee;">Prevents System Failure</td>
            </tr>
        </tbody>
    </table>
</div>
`;

    // 3. Map Utility (Integrating with user's enabled Maps API)
    let mapEmbedHtml = '';
    if (apiKey) {
        if (flags.show_live_map) mapEmbedHtml += maps.generateMapEmbed(apiKey, location);
        if (flags.show_static_map) mapEmbedHtml += maps.generateStaticMap(apiKey, location);
        if (flags.show_street_view) mapEmbedHtml += maps.generateStreetView(apiKey, location);
        if (flags.show_directions) mapEmbedHtml += maps.generateDirectionsLink(location, businessAddress);
        if (flags.show_reviews && placeId) mapEmbedHtml += maps.generatePlaceReview(apiKey, placeId);
    } else {
        mapEmbedHtml = `
<div class="map-feature" style="margin: 30px 0; border-radius: 12px; overflow: hidden; background: #eee; min-height: 300px; display: flex; align-items: center; justify-content: center; border: 1px solid #ddd; padding: 20px;">
    <div style="text-align: center; color: #666;">
        <p style="margin-bottom: 10px; font-weight: bold;">Google Maps Data Layer Integrated</p>
        <p style="font-size: 0.8rem;">(Waiting for API verification to activate live view)</p>
    </div>
</div>
`;
    }

    // 4. Narrative Content
    const bodyText = `
<div class="article-body">
    <p>As we transition into the warmer months in ${location}, ensuring your air conditioning system is ready for the intense desert heat is critical. A proactive approach to Spring maintenance can prevent emergency breakdowns during peak July temperatures.</p>
    
    ${statsHtml}

    <h2>Why Local Lancaster Homeowners Prioritize Spring Maintenance</h2>
    <p>In the Antelope Valley, dust and high winds often lead to premature coil clogging and reduced airflow. Our local technicians emphasize that a simple 21-point inspection in April or May can save up to 30% on cooling costs throughout the summer season.</p>
    
    ${mapEmbedHtml}
    
    ${tableHtml}

    <p>Don't wait for your system to fail on a triple-digit afternoon. Contact Working Class HVAC today for a comprehensive local assessment.</p>
</div>
`;

    return bodyText;
}

module.exports = {
    getEnrichedContent
};
