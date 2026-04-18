(function () {
    if (typeof Chart === "undefined") {
        return;
    }

    const labelsNode = document.getElementById("chart-labels");
    const valuesNode = document.getElementById("chart-values");
    const canvas = document.getElementById("paymentsChart");

    if (labelsNode && valuesNode && canvas) {
        const labels = JSON.parse(labelsNode.textContent);
        const values = JSON.parse(valuesNode.textContent);

        new Chart(canvas, {
            type: "doughnut",
            data: {
                labels: labels,
                datasets: [
                    {
                        data: values,
                        backgroundColor: ["#16a34a", "#f59e0b", "#dc2626"],
                        borderWidth: 0,
                    },
                ],
            },
            options: {
                plugins: {
                    legend: {
                        position: "bottom",
                    },
                },
                cutout: "65%",
            },
        });
    }

    const revenueLabelsNode = document.getElementById("revenue-chart-labels");
    const revenueValuesNode = document.getElementById("revenue-chart-values");
    const revenueCanvas = document.getElementById("revenueChart");

    if (revenueLabelsNode && revenueValuesNode && revenueCanvas) {
        const revenueLabels = JSON.parse(revenueLabelsNode.textContent);
        const revenueValues = JSON.parse(revenueValuesNode.textContent);

        new Chart(revenueCanvas, {
            type: "bar",
            data: {
                labels: revenueLabels,
                datasets: [
                    {
                        label: "Revenue",
                        data: revenueValues,
                        borderRadius: 8,
                        backgroundColor: "rgba(13, 110, 253, 0.75)",
                        borderColor: "rgba(13, 110, 253, 1)",
                        borderWidth: 1,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function (value) {
                                return "INR " + value;
                            },
                        },
                    },
                },
                plugins: {
                    legend: {
                        display: false,
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return "Revenue: INR " + context.parsed.y;
                            },
                        },
                    },
                },
            },
        });
    }
})();
