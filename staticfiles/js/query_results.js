function initGradeTrendChart() {
        // 成绩趋势图
    const gradesCtx = document.getElementById('gradesChart').getContext('2d');
    const gradesChart = new Chart(gradesCtx, {
        type: 'line',
        data: {
            labels: ['2024春季', '2024秋季', '2025春季'],
            datasets: [{
                label: 'GPA',
                data: [3.65, 3.78, 3.92],
                borderColor: 'rgba(13, 110, 253, 1)',
                backgroundColor: 'rgba(13, 110, 253, 0.1)',
                tension: 0.3,
                fill: true
            }, {
                label: '平均分',
                data: [84.5, 86.2, 88.5],
                borderColor: 'rgba(25, 135, 84, 1)',
                backgroundColor: 'transparent',
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    min: 60,
                    max: 100,
                    ticks: {
                        callback: function (value) {
                            return value;
                        }
                    }
                }
            }
        }
    });

    // 成绩分布图
    const distributionCtx = document.getElementById('gradeDistribution').getContext('2d');
    const distributionChart = new Chart(distributionCtx, {
        type: 'bar',
        data: {
            labels: ['90-100', '80-89', '70-79', '60-69', '60以下'],
            datasets: [{
                label: '课程数量',
                data: [6, 4, 1, 0, 0],
                backgroundColor: [
                    'rgba(25, 135, 84, 0.8)',
                    'rgba(13, 110, 253, 0.8)',
                    'rgba(255, 193, 7, 0.8)',
                    'rgba(220, 53, 69, 0.8)',
                    'rgba(108, 117, 125, 0.8)'
                ],
                borderColor: [
                    'rgba(25, 135, 84, 1)',
                    'rgba(13, 110, 253, 1)',
                    'rgba(255, 193, 7, 1)',
                    'rgba(220, 53, 69, 1)',
                    'rgba(108, 117, 125, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });

    // 分数分布图 (Modal)
    const scoreDistCtx = document.getElementById('scoreDistributionChart').getContext('2d');
    const scoreDistChart = new Chart(scoreDistCtx, {
        type: 'bar',
        data: {
            labels: ['60-69', '70-79', '80-89', '90-100'],
            datasets: [{
                label: '学生人数',
                data: [5, 25, 60, 30],
                backgroundColor: 'rgba(13, 110, 253, 0.6)',
                borderColor: 'rgba(13, 110, 253, 1)',
                borderWidth: 1
            }, {
                label: '你的成绩',
                data: [0, 0, 0, 95],
                backgroundColor: 'rgba(220, 53, 69, 0.6)',
                borderColor: 'rgba(220, 53, 69, 1)',
                borderWidth: 1,
                barPercentage: 0.2,
                categoryPercentage: 0.5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}
window.onload = initGradeTrendChart;