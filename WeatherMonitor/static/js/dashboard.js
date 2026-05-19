document.addEventListener('DOMContentLoaded', function() {
    // Update the last update time display
    console.log('Dashboard.js loaded');
    function updateLastUpdateTime() {
        const now = new Date();
        const hours = now.getHours().toString().padStart(2, '0');
        const minutes = now.getMinutes().toString().padStart(2, '0');
        const seconds = now.getSeconds().toString().padStart(2, '0');
        
        const timeDisplay = document.getElementById('last-update-time');
        if (timeDisplay) {
            timeDisplay.textContent = `${hours}:${minutes}:${seconds}`;
        }
    }
    
    // Run the update time function immediately and set interval
    updateLastUpdateTime();
    setInterval(updateLastUpdateTime, 5000);
    
    // Generate and display sample chart data immediately
    generateSampleChartData();
    
    // Generate sample chart data for demonstration
    function generateSampleChartData() {
        console.log('Generating sample data');
        console.log("Air Quality Chart Canvas:", document.getElementById('airQualityChart'));
        console.log("Humidity Chart Canvas:", document.getElementById('humidityChart'));
        console.log("Temperature Chart Canvas:", document.getElementById('temperatureChart'));
        console.log("Rainfall Chart Canvas:", document.getElementById('rainfallChart'));
        
        const hours = 24;
        const now = new Date();
        const temperatureData = [];
        const humidityData = [];
        const airQualityData = [];
        const rainfallData = [];
        const labels = [];
        
        // Generate data points for the last 24 hours
        for (let i = hours; i >= 0; i--) {
            const time = new Date(now.getTime() - i * 60 * 60 * 1000);
            
            // Format time label using the function from charts.js
            labels.push(formatDateForChart(time, 'time'));
            
            // Generate semi-random data points with a daily cycle pattern
            // Temperature varies between 18-28°C with a daily cycle
            const baseTemp = 23;
            const hourVariation = 5 * Math.sin((time.getHours() + 6) * (Math.PI / 12));
            const randomVariation = Math.random() * 2 - 1;
            temperatureData.push(baseTemp + hourVariation + randomVariation);
            
            // Humidity varies between 40-70% with an inverse cycle to temperature
            const baseHumidity = 55;
            const humidityVariation = -15 * Math.sin((time.getHours() + 6) * (Math.PI / 12));
            const humidityRandom = Math.random() * 5 - 2.5;
            humidityData.push(baseHumidity + humidityVariation + humidityRandom);
            
            // Air quality varies between 50-300 PPM with more realistic values
            const baseAirQuality = 150;
            const airQualityVariation = 100 * Math.sin((time.getHours() + 3) * (Math.PI / 12));
            const airQualityRandom = Math.random() * 50 - 25;
            const airQualityValue = Math.max(50, Math.min(300, baseAirQuality + airQualityVariation + airQualityRandom));
            airQualityData.push(airQualityValue);

            // Generate rainfall data (0-25mm with some random variation)
            const baseRainfall = Math.max(0, 5 * Math.sin((time.getHours() + 3) * (Math.PI / 12)));
            const rainfallRandom = Math.random() * 2;
            rainfallData.push(Math.round((baseRainfall + rainfallRandom) * 10) / 10);
        }
        
        // Create charts using the functions from charts.js
        createTemperatureChart('temperatureChart', labels, temperatureData);
        createHumidityChart('humidityChart', labels, humidityData);
        
        // Create Air Quality Chart
        const airQualityChartCanvas = document.getElementById('airQualityChart');
        if (airQualityChartCanvas) {
            createAirQualityChart('airQualityChart', labels, airQualityData, {
                yAxisMin: 0,
                yAxisMax: 300,
                borderColor: 'rgba(255, 193, 7, 1)',
                backgroundColor: 'rgba(255, 193, 7, 0.2)',
                title: 'Air Quality (PPM)',
                tension: 0.3
            });
        }
        
        // Create Rainfall Chart
        const rainfallChartCanvas = document.getElementById('rainfallChart');
        if (rainfallChartCanvas) {
            const existingChart = Chart.getChart(rainfallChartCanvas);
            if (existingChart) {
                existingChart.destroy();
            }
            
            createRainfallChart('rainfallChart', labels, rainfallData, {
                yAxisMin: 0,
                yAxisMax: 25,
                borderColor: 'rgba(0, 156, 255, 1)',
                backgroundColor: 'rgba(0, 156, 255, 0.2)',
                title: 'Rainfall (mm)',
                tension: 0.3
            });
        }
            
    }

    // Initialisation de la carte Leaflet si l'élément existe
    var mapDiv = document.getElementById('map');
    if (mapDiv) {
        var map = L.map('map').setView([33.5731, -7.5898], 12); // Centré sur Casablanca
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map);
        // Récupération des capteurs depuis une variable globale injectée par Flask
        if (window.capteurs && Array.isArray(window.capteurs)) {
            window.capteurs.forEach(function(capteur) {
                L.marker([capteur.lat, capteur.lng]).addTo(map)
                    .bindPopup('<b>' + capteur.nom + '</b><br>Température : ' + capteur.temp + '°C');
            });
        }
    }
})