document.addEventListener('DOMContentLoaded', function () {
    const pieChartData = {
        labels: ['Late', 'On Time'],
        datasets: [{
            data: [window.attendanceSummary.late, window.attendanceSummary.onTime],
            backgroundColor: ['#FF6384', '#36A2EB']
        }]
    };

    const pieChartConfig = {
        type: 'pie',
        data: pieChartData,
    };

    const pieChart = new Chart(
        document.getElementById('pieChart'),
        pieChartConfig
    );

    const stackedChartData = {
        labels: ['Late', 'On Time'],
        datasets: [{
            label: 'Attendance Status',
            data: [window.attendanceSummary.late, window.attendanceSummary.onTime],
            backgroundColor: ['#FF6384', '#36A2EB'],
        }]
    };

    const stackedChartConfig = {
        type: 'bar',
        data: stackedChartData,
        options: {
            scales: {
                x: { stacked: true },
                y: { stacked: true }
            }
        }
    };

    const stackedChart = new Chart(
        document.getElementById('stackedChart'),
        stackedChartConfig
    );
});
