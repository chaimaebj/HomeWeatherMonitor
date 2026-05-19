// charts.js - Utility functions for creating and updating charts in HomeWeather

/**
 * Creates a temperature chart with the given data
 * @param {string} elementId - Canvas element ID
 * @param {array} labels - Array of time labels
 * @param {array} data - Array of temperature values
 * @param {object} options - Optional configuration options
 */
function createTemperatureChart(elementId, labels, data, options = {}) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return null;
    
    // Default configuration
    const defaultOptions = {
        yAxisMin: 10,
        yAxisMax: 35,
        borderColor: 'rgba(220, 53, 69, 1)',
        backgroundColor: 'rgba(220, 53, 69, 0.2)',
        title: 'Temperature (°C)'
    };
    
    // Merge options
    const chartOptions = { ...defaultOptions, ...options };
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: chartOptions.title,
                data: data,
                backgroundColor: chartOptions.backgroundColor,
                borderColor: chartOptions.borderColor,
                borderWidth: 2,
                tension: 0.3,
                pointRadius: 1,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    min: chartOptions.yAxisMin,
                    max: chartOptions.yAxisMax,
                    title: {
                        display: true,
                        text: chartOptions.title
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    },
                    ticks: {
                        maxTicksLimit: 8
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${chartOptions.title}: ${context.parsed.y}`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Creates a humidity chart with the given data
 * @param {string} elementId - Canvas element ID
 * @param {array} labels - Array of time labels
 * @param {array} data - Array of humidity values
 * @param {object} options - Optional configuration options
 */
function createHumidityChart(elementId, labels, data, options = {}) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return null;
    
    // Default configuration
    const defaultOptions = {
        yAxisMin: 30,
        yAxisMax: 80,
        borderColor: 'rgba(13, 110, 253, 1)',
        backgroundColor: 'rgba(13, 110, 253, 0.2)',
        title: 'Humidity (%)'
    };
    
    // Merge options
    const chartOptions = { ...defaultOptions, ...options };
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: chartOptions.title,
                data: data,
                backgroundColor: chartOptions.backgroundColor,
                borderColor: chartOptions.borderColor,
                borderWidth: 2,
                tension: 0.3,
                pointRadius: 1,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    min: chartOptions.yAxisMin,
                    max: chartOptions.yAxisMax,
                    title: {
                        display: true,
                        text: chartOptions.title
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    },
                    ticks: {
                        maxTicksLimit: 8
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${chartOptions.title}: ${context.parsed.y}`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Creates an air quality chart with the given data
 * @param {string} elementId - Canvas element ID
 * @param {array} labels - Array of time labels
 * @param {array} data - Array of air quality values
 * @param {object} options - Optional configuration options
 */
function createAirQualityChart(elementId, labels, data, options = {}) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return null;
    
    // Default configuration
    const defaultOptions = {
        yAxisMin: 0,
        yAxisMax: 400,
        borderColor: 'rgba(255, 193, 7, 1)',
        backgroundColor: 'rgba(255, 193, 7, 0.2)',
        title: 'Air Quality (PPM)'
    };
    
    // Merge options
    const chartOptions = { ...defaultOptions, ...options };
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: chartOptions.title,
                data: data,
                backgroundColor: chartOptions.backgroundColor,
                borderColor: chartOptions.borderColor,
                borderWidth: 2,
                tension: 0.3,
                pointRadius: 1,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    min: chartOptions.yAxisMin,
                    max: chartOptions.yAxisMax,
                    title: {
                        display: true,
                        text: chartOptions.title
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    },
                    ticks: {
                        maxTicksLimit: 8
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${chartOptions.title}: ${context.parsed.y}`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Creates a multi-parameter chart with the given data
 * @param {string} elementId - Canvas element ID
 * @param {array} labels - Array of time labels
 * @param {array} datasets - Array of datasets
 * @param {object} options - Optional configuration options
 */
function createMultiChart(elementId, labels, datasets, options = {}) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return null;
    
    // Default configuration
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Value'
                }
            },
            x: {
                title: {
                    display: true,
                    text: 'Time'
                },
                ticks: {
                    maxTicksLimit: 8
                }
            }
        },
        plugins: {
            legend: {
                position: 'top'
            }
        }
    };
    
    // Merge options
    const chartOptions = { ...defaultOptions, ...options };
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: chartOptions
    });
}

/**
 * Creates a pie chart for displaying percentages or counts
 * @param {string} elementId - Canvas element ID 
 * @param {array} labels - Array of category labels
 * @param {array} data - Array of values
 * @param {array} backgroundColor - Array of background colors
 * @param {string} title - Chart title
 */
function createPieChart(elementId, labels, data, backgroundColor, title = '') {
    const ctx = document.getElementById(elementId);
    if (!ctx) return null;
    
    return new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: backgroundColor
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: title !== '',
                    text: title
                }
            }
        }
    });
}

/**
 * Format date objects for chart labels
 * @param {Date} date - Date object to format
 * @param {string} format - Format type: 'time', 'date', 'datetime'
 * @returns {string} - Formatted date string
 */
function formatDateForChart(date, format = 'time') {
    if (!(date instanceof Date)) {
        return '';
    }
    
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    
    switch (format) {
        case 'time':
            return `${hours}:${minutes}`;
        case 'date':
            return `${day}/${month}`;
        case 'datetime':
            return `${day}/${month} ${hours}:${minutes}`;
        default:
            return `${hours}:${minutes}`;
    }
}

/**
 * Creates a rainfall chart with the given data
 * @param {string} elementId - Canvas element ID
 * @param {array} labels - Array of time labels
 * @param {array} data - Array of rainfall values
 * @param {object} options - Optional configuration options
 */
function createRainfallChart(elementId, labels, data, options = {}) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return null;
    
    // Default configuration
    const defaultOptions = {
        yAxisMin: 0,
        yAxisMax: 25,
        borderColor: 'rgba(0, 156, 255, 1)',
        backgroundColor: 'rgba(0, 156, 255, 0.2)',
        title: 'Rainfall (mm)'
    };
    
    // Merge options
    const chartOptions = { ...defaultOptions, ...options };
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: chartOptions.title,
                data: data,
                backgroundColor: chartOptions.backgroundColor,
                borderColor: chartOptions.borderColor,
                borderWidth: 2,
                tension: 0.3,
                pointRadius: 1,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    min: chartOptions.yAxisMin,
                    max: chartOptions.yAxisMax,
                    title: {
                        display: true,
                        text: chartOptions.title
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    },
                    ticks: {
                        maxTicksLimit: 8
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${chartOptions.title}: ${context.parsed.y}`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Creates a multi-parameter chart with the given data
 * @param {string} elementId - Canvas element ID
 * @param {array} labels - Array of time labels
 * @param {array} datasets - Array of datasets
 * @param {object} options - Optional configuration options
 */
function createMultiChart(elementId, labels, datasets, options = {}) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return null;
    
    // Default configuration
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Value'
                }
            },
            x: {
                title: {
                    display: true,
                    text: 'Time'
                },
                ticks: {
                    maxTicksLimit: 8
                }
            }
        },
        plugins: {
            legend: {
                position: 'top'
            }
        }
    };
    
    // Merge options
    const chartOptions = { ...defaultOptions, ...options };
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: chartOptions
    });
}

/**
 * Creates a pie chart for displaying percentages or counts
 * @param {string} elementId - Canvas element ID 
 * @param {array} labels - Array of category labels
 * @param {array} data - Array of values
 * @param {array} backgroundColor - Array of background colors
 * @param {string} title - Chart title
 */
function createPieChart(elementId, labels, data, backgroundColor, title = '') {
    const ctx = document.getElementById(elementId);
    if (!ctx) return null;
    
    return new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: backgroundColor
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: title !== '',
                    text: title
                }
            }
        }
    });
}

/**
 * Format date objects for chart labels
 * @param {Date} date - Date object to format
 * @param {string} format - Format type: 'time', 'date', 'datetime'
 * @returns {string} - Formatted date string
 */
function formatDateForChart(date, format = 'time') {
    if (!(date instanceof Date)) {
        return '';
    }
    
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    
    switch (format) {
        case 'time':
            return `${hours}:${minutes}`;
        case 'date':
            return `${day}/${month}`;
        case 'datetime':
            return `${day}/${month} ${hours}:${minutes}`;
        default:
            return `${hours}:${minutes}`;
    }
}
