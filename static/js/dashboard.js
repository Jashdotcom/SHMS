(function () {
    const labelsNode = document.getElementById("chart-labels");
    const valuesNode = document.getElementById("chart-values");
    const canvas = document.getElementById("paymentsChart");

    if (!labelsNode || !valuesNode || !canvas || typeof Chart === "undefined") {
        return;
    }

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
})();
