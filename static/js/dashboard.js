(function () {
    if (typeof Chart === "undefined") {
        return;
    }

    function readJson(id) {
        const node = document.getElementById(id);
        return node ? JSON.parse(node.textContent) : null;
    }

    const paymentLabels = readJson("payment-chart-labels");
    const paymentValues = readJson("payment-chart-values");
    const paymentCanvas = document.getElementById("paymentsChart");

    if (paymentLabels && paymentValues && paymentCanvas) {
        new Chart(paymentCanvas, {
            type: "doughnut",
            data: {
                labels: paymentLabels,
                datasets: [
                    {
                        data: paymentValues,
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

    const bookingTrendLabels = readJson("monthly-bookings-labels");
    const bookingTrendValues = readJson("monthly-bookings-values");
    const bookingTrendCanvas = document.getElementById("bookingsTrendChart");

    if (bookingTrendLabels && bookingTrendValues && bookingTrendCanvas) {
        new Chart(bookingTrendCanvas, {
            type: "line",
            data: {
                labels: bookingTrendLabels,
                datasets: [
                    {
                        label: "Bookings",
                        data: bookingTrendValues,
                        borderColor: "rgba(0, 166, 166, 1)",
                        backgroundColor: "rgba(0, 166, 166, 0.16)",
                        tension: 0.35,
                        fill: true,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false,
                    },
                },
            },
        });
    }

    const paymentTrendLabels = readJson("monthly-payments-labels");
    const paymentTrendValues = readJson("monthly-payments-values");
    const paymentTrendCanvas = document.getElementById("paymentsTrendChart");

    if (paymentTrendLabels && paymentTrendValues && paymentTrendCanvas) {
        new Chart(paymentTrendCanvas, {
            type: "bar",
            data: {
                labels: paymentTrendLabels,
                datasets: [
                    {
                        label: "Collected Payments",
                        data: paymentTrendValues,
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
                                return "Collected: INR " + context.parsed.y;
                            },
                        },
                    },
                },
            },
        });
    }
})();
