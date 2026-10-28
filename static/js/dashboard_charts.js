document.addEventListener("DOMContentLoaded", function () {
    const trendCtx = document.getElementById("revenueTrendChart")?.getContext("2d");
    const paymentCtx = document.getElementById("paymentModeChart")?.getContext("2d");

    if (!trendCtx || !paymentCtx) return;

    fetch("/dashboard/api/sales-chart/")
        .then(res => res.json())
        .then(data => {
            // 1. Line Chart for Revenue Trend
            new Chart(trendCtx, {
                type: "line",
                data: {
                    labels: data.revenue_trend.labels,
                    datasets: [{
                        label: "Revenue (₹)",
                        data: data.revenue_trend.data,
                        borderColor: "#4F46E5",
                        backgroundColor: "rgba(79, 70, 229, 0.08)",
                        borderWidth: 2.5,
                        fill: true,
                        tension: 0.35,
                        pointBackgroundColor: "#4F46E5",
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: ctx => ` Sales: ₹${ctx.raw.toFixed(2)}`
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { color: "#F1F5F9" },
                            ticks: {
                                callback: val => '₹' + val
                            }
                        },
                        x: {
                            grid: { display: false }
                        }
                    }
                }
            });

            // 2. Doughnut Chart for Payment Modes
            new Chart(paymentCtx, {
                type: "doughnut",
                data: {
                    labels: data.payment_methods.labels,
                    datasets: [{
                        data: data.payment_methods.data,
                        backgroundColor: [
                            "#10B981", // Cash (Green)
                            "#3B82F6", // UPI (Blue)
                            "#EF4444", // Khata/Udhar (Red)
                            "#F59E0B"  // Split/Other
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                boxWidth: 12,
                                padding: 14,
                                font: { size: 12 }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: ctx => ` ${ctx.label}: ₹${ctx.raw.toFixed(2)}`
                            }
                        }
                    },
                    cutout: "65%"
                }
            });
        })
        .catch(err => {
            console.error("Failed to load dashboard chart data:", err);
        });
});
