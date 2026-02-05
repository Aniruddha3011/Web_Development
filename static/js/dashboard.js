// Dashboard JavaScript - displays analysis results with charts

const API_BASE = ''; // Use relative paths for Vercel stability

let currentResults = null;
let barChart = null;
let pieChart = null;

document.addEventListener('DOMContentLoaded', async () => {
    const sessionId = localStorage.getItem('sessionId');
    const sessionType = localStorage.getItem('sessionType'); // 'creator' or 'single'

    if (!sessionId) {
        window.location.href = '/';
        return;
    }

    if (sessionType === 'creator') {
        loadCreatorAnalysis(sessionId);
    } else {
        await loadAnalysis(sessionId);
    }

    setupEventListeners();
});

async function loadCreatorAnalysis(sessionId) {
    // Try localStorage first
    const localFullData = localStorage.getItem('creatorFullData');
    if (localFullData) {
        const fullData = JSON.parse(localFullData);
        // Hide standard report, show creator report
        document.getElementById('standardReport').style.display = 'none';
        document.getElementById('creatorReport').style.display = 'block';

        displayCreatorResults(fullData);
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/session/${sessionId}`);
        const data = await response.json();

        if (response.ok) {
            // Hide standard report, show creator report
            document.getElementById('standardReport').style.display = 'none';
            document.getElementById('creatorReport').style.display = 'block';

            displayCreatorResults(data.data); // data structure matches app.py response
        } else {
            alert('Session not found.');
            window.location.href = '/';
        }
    } catch (error) {
        console.error(error);
        alert('Error loading report');
    }
}

function displayCreatorResults(data) {
    const { creator_name, timestamp, business_analysis, stats } = data;

    // Header
    document.getElementById('creatorNameDisplay').textContent = creator_name;
    document.getElementById('reportTime').textContent = `Generated on ${new Date(timestamp).toLocaleString()}`;

    // Show Errors if any
    const errorBox = document.getElementById('scrapingErrors');
    const errorList = document.getElementById('errorList');
    if (data.errors && data.errors.length > 0) {
        errorBox.style.display = 'block';
        errorList.innerHTML = data.errors.map(err => `<li>${escapeHtml(err)}</li>`).join('');
        // Highlight why it might be empty
        if (data.stats.total_count === 0) {
            errorList.innerHTML += `<li style="margin-top:0.5rem; font-weight:bold;">💡 Tip: If the fetch failed, try double-checking the URL or wait a moment and try again.</li>`;
        }
    } else {
        errorBox.style.display = 'none';
    }

    // Main Rec
    const recBox = document.getElementById('recBox');
    const recTitle = document.getElementById('recTitle');
    document.getElementById('recDetail').textContent = business_analysis.recommendation_detail;
    document.getElementById('safetyScore').textContent = `${business_analysis.overall_score}%`;
    document.getElementById('cultLevel').textContent = business_analysis.cult_following_indicator;

    document.getElementById('recTitle').textContent = business_analysis.recommendation_title;

    // Styling based on category
    if (business_analysis.category === 'excellent') {
        recBox.style.background = 'rgba(16, 185, 129, 0.1)';
        recBox.style.borderColor = '#10b981';
        recTitle.style.color = '#10b981';
    } else if (business_analysis.category === 'good') {
        recBox.style.background = 'rgba(245, 158, 11, 0.1)';
        recBox.style.borderColor = '#f59e0b';
        recTitle.style.color = '#f59e0b';
    } else {
        recBox.style.background = 'rgba(239, 68, 68, 0.1)';
        recBox.style.borderColor = '#ef4444';
        recTitle.style.color = '#ef4444';
    }

    // Platform stats
    updatePlatformScore('ytScore', stats.platform_breakdown.youtube);
    updatePlatformScore('redditScore', stats.platform_breakdown.reddit);

    // --- POPULATE GLOBAL STATS & CHARTS ---
    const counts = {
        positive: stats.positive.length,
        negative: stats.negative.length,
        neutral: stats.neutral.length,
        total: stats.total_count
    };

    // Update stat cards
    document.getElementById('positiveCount').textContent = counts.positive;
    document.getElementById('negativeCount').textContent = counts.negative;
    document.getElementById('neutralCount').textContent = counts.neutral;
    document.getElementById('totalCount').textContent = counts.total;

    // Create charts
    createBarChart(counts);
    createPieChart(counts);

    // Set global currentResults for comment filtering
    currentResults = stats;
    displayComments('positive');
}

function updatePlatformScore(elementId, stats) {
    const el = document.getElementById(elementId);
    if (stats.total === 0) {
        el.textContent = "N/A";
        el.style.color = "#64748b";
        return;
    }
    // Calculate safely
    const safe = ((stats.positive + stats.neutral) / stats.total) * 100;
    el.textContent = `${safe.toFixed(1)}%`;
}

// Keep original loadAnalysis function below...
async function loadAnalysis(sessionId) {
    // First, try loading from localStorage as it's the most reliable on Vercel
    const localResults = localStorage.getItem('analysisResults');
    if (localResults) {
        console.log("Loading from localStorage...");
        currentResults = JSON.parse(localResults);
        displayResults({
            title: 'Sentiment Analysis Result',
            timestamp: new Date().toISOString(),
            results: currentResults
        });
        return;
    }

    // Fallback: Try API if localStorage is empty
    try {
        const response = await fetch(`${API_BASE}/api/session/${sessionId}`);
        if (response.ok) {
            const data = await response.json();
            currentResults = data.results;
            displayResults(data);
        } else {
            alert('Session not found. Redirecting to home...');
            window.location.href = '/';
        }
    } catch (error) {
        console.error("API Fetch Error:", error);
        alert('Error loading analysis: ' + error.message);
        window.location.href = '/';
    }
}

function displayResults(data) {
    const title = data.title || 'Sentiment Analysis Result';
    const timestamp = data.timestamp || new Date().toISOString();
    const results = data.results;

    // Standardize counts: Check in results.counts or results directly
    let counts = results.counts || {
        positive: (results.positive || []).length,
        negative: (results.negative || []).length,
        neutral: (results.neutral || []).length,
        total: (results.positive || []).length + (results.negative || []).length + (results.neutral || []).length
    };

    // Update title and timestamp
    document.getElementById('analysisTitle').textContent = title;
    document.getElementById('analysisTime').textContent =
        `Analyzed on ${new Date(timestamp).toLocaleString()}`;

    // Update Brand Score
    if (results.brand_score !== undefined) {
        const scoreContainer = document.getElementById('brandScoreContainer');
        const scoreValue = document.getElementById('brandScoreValue');
        const scoreBar = document.getElementById('brandScoreBar');
        const recommendation = document.getElementById('brandRecommendation');

        scoreContainer.style.display = 'block';
        scoreValue.textContent = `${results.brand_score}%`;
        scoreBar.style.width = `${results.brand_score}%`;
        recommendation.textContent = results.brand_recommendation;

        // Color coding for recommendation
        if (results.brand_score > 80) {
            recommendation.style.color = '#10b981'; // Green
            recommendation.style.border = '1px solid #10b981';
        } else {
            recommendation.style.color = '#f59e0b'; // Orange/Yellow
            recommendation.style.border = '1px solid #f59e0b';
        }
    }

    // Update stat cards
    document.getElementById('positiveCount').textContent = counts.positive;
    document.getElementById('negativeCount').textContent = counts.negative;
    document.getElementById('neutralCount').textContent = counts.neutral;
    document.getElementById('totalCount').textContent = counts.total;

    // Create charts
    createBarChart(counts);
    createPieChart(counts);

    // Display comments (default: positive)
    displayComments('positive');
}

function createBarChart(counts) {
    const ctx = document.getElementById('barChart').getContext('2d');

    if (barChart) {
        barChart.destroy();
    }

    barChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Positive', 'Negative', 'Neutral'],
            datasets: [{
                label: 'Number of Comments',
                data: [counts.positive, counts.negative, counts.neutral],
                backgroundColor: [
                    'rgba(16, 185, 129, 0.8)',  // Green
                    'rgba(239, 68, 68, 0.8)',   // Red
                    'rgba(245, 158, 11, 0.8)'   // Orange
                ],
                borderColor: [
                    'rgba(16, 185, 129, 1)',
                    'rgba(239, 68, 68, 1)',
                    'rgba(245, 158, 11, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#94a3b8'
                    },
                    grid: {
                        color: '#334155'
                    }
                },
                x: {
                    ticks: {
                        color: '#94a3b8'
                    },
                    grid: {
                        color: '#334155'
                    }
                }
            }
        }
    });
}

function createPieChart(counts) {
    const ctx = document.getElementById('pieChart').getContext('2d');

    if (pieChart) {
        pieChart.destroy();
    }

    pieChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Positive', 'Negative', 'Neutral'],
            datasets: [{
                data: [counts.positive, counts.negative, counts.neutral],
                backgroundColor: [
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(245, 158, 11, 0.8)'
                ],
                borderColor: [
                    'rgba(16, 185, 129, 1)',
                    'rgba(239, 68, 68, 1)',
                    'rgba(245, 158, 11, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#94a3b8',
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function displayComments(sentiment) {
    const container = document.getElementById('commentsContainer');
    const comments = currentResults[sentiment];

    if (!comments || comments.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #94a3b8;">No comments in this category</p>';
        return;
    }

    container.innerHTML = comments.map(comment => `
        <div class="comment-item ${sentiment}">
            ${escapeHtml(comment)}
        </div>
    `).join('');
}

function setupEventListeners() {
    // Sentiment filter
    document.getElementById('sentimentFilter').addEventListener('change', (e) => {
        displayComments(e.target.value);
    });

    // Back button
    document.getElementById('backBtn').addEventListener('click', () => {
        window.location.href = '/';
    });

    // New analysis button
    document.getElementById('newAnalysisBtn').addEventListener('click', () => {
        localStorage.removeItem('sessionId');
        window.location.href = '/';
    });

    // Export button
    document.getElementById('exportBtn').addEventListener('click', () => {
        exportResults();
    });
}

async function exportResults() {
    if (!currentResults) {
        alert("No results found to export. Please run an analysis first.");
        return;
    }

    try {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();

        // Handle different data structures (Creator vs Single)
        let counts = {};
        let resultsObj = currentResults;

        // Normalize results for the PDF
        if (currentResults.stats) {
            // Creator analytics structure
            counts = {
                positive: (currentResults.positive || []).length,
                negative: (currentResults.negative || []).length,
                neutral: (currentResults.neutral || []).length,
                total: currentResults.total_count || 0
            };
        } else {
            // Single analysis structure
            counts = {
                positive: (currentResults.positive || []).length,
                negative: (currentResults.negative || []).length,
                neutral: (currentResults.neutral || []).length,
                total: ((currentResults.positive || []).length + (currentResults.negative || []).length + (currentResults.neutral || []).length)
            };
        }

        const titleText = document.getElementById('analysisTitle')?.textContent || 'Sentiment Analysis Report';

        // --- PDF DESIGN ---
        // Header
        doc.setFontSize(22);
        doc.setTextColor(67, 79, 235);
        doc.text('Sentiment Analysis Report', 105, 20, { align: 'center' });

        doc.setDrawColor(67, 79, 235);
        doc.setLineWidth(0.5);
        doc.line(14, 25, 196, 25);

        doc.setFontSize(12);
        doc.setTextColor(60, 60, 60);
        doc.text(`Title: ${titleText}`, 14, 35);
        doc.text(`Date: ${new Date().toLocaleString()}`, 14, 42);

        // Summary Statistics Table
        doc.autoTable({
            startY: 50,
            head: [['Sentiment Metric', 'Count/Value']],
            body: [
                ['Positive Comments', counts.positive],
                ['Negative Comments', counts.negative],
                ['Neutral Comments', counts.neutral],
                ['Total Analyzed', counts.total],
                ['Success Rate', counts.total > 0 ? `${((counts.positive / counts.total) * 100).toFixed(1)}%` : '0%']
            ],
            theme: 'striped',
            headStyles: { fillColor: [67, 79, 235] }
        });

        // Capture Charts (if visible)
        const barCanvas = document.getElementById('barChart');
        if (barCanvas) {
            try {
                const barImg = barCanvas.toDataURL('image/png', 1.0);
                doc.addPage();
                doc.setFontSize(16);
                doc.setTextColor(67, 79, 235);
                doc.text('Visual Sentiment Distribution', 14, 20);
                doc.addImage(barImg, 'PNG', 15, 30, 180, 90);

                const pieCanvas = document.getElementById('pieChart');
                if (pieCanvas) {
                    const pieImg = pieCanvas.toDataURL('image/png', 1.0);
                    doc.text('Sentiment Breakdown (%)', 14, 135);
                    doc.addImage(pieImg, 'PNG', 55, 140, 100, 100);
                }
            } catch (chartErr) {
                console.warn("Chart capture failed, skipping charts in PDF:", chartErr);
            }
        }

        // Detailed Comments Table (Sample)
        doc.addPage();
        doc.setFontSize(16);
        doc.setTextColor(67, 79, 235);
        doc.text('Comment Details (Sample)', 14, 20);

        const tableBody = [];
        ['positive', 'negative', 'neutral'].forEach(sentiment => {
            const comments = resultsObj[sentiment] || [];
            comments.slice(0, 20).forEach(comment => {
                tableBody.push([sentiment.toUpperCase(), comment]);
            });
        });

        if (tableBody.length > 0) {
            doc.autoTable({
                startY: 30,
                head: [['Sentiment', 'Comment Text']],
                body: tableBody.slice(0, 100),
                styles: { fontSize: 8, cellPadding: 2, overflow: 'linebreak' },
                columnStyles: {
                    0: { cellWidth: 25, fontStyle: 'bold' },
                    1: { cellWidth: 'auto' }
                }
            });
        } else {
            doc.setFontSize(10);
            doc.setTextColor(100, 100, 100);
            doc.text('No detailed comments available for export.', 14, 30);
        }

        // Page Numbering Footer
        const pageCount = doc.internal.getNumberOfPages();
        for (let i = 1; i <= pageCount; i++) {
            doc.setPage(i);
            doc.setFontSize(8);
            doc.setTextColor(150, 150, 150);
            doc.text(`Page ${i} of ${pageCount} | Universal Sentiment Analysis Project`, 105, 290, { align: 'center' });
        }

        doc.save(`${titleText.replace(/[^a-z0-9]/gi, '_')}_Report.pdf`);
    } catch (err) {
        console.error("PDF Export Error:", err);
        alert("Attention: Failed to generate PDF. Falling back to CSV.");
        // Simple CSV fallback
        const counts = currentResults.counts || { positive: 0, negative: 0, neutral: 0, total: 0 };
        let csv = 'Sentiment,Count\n';
        csv += `Positive,${counts.positive}\nNegative,${counts.negative}\nNeutral,${counts.neutral}\n`;
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'sentiment_report.csv';
        a.click();
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
