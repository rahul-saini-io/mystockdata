$(document).ready(function() {
    let portfolioChart = null;
    
    // Load dashboard data
    loadDashboardStats();

    function loadDashboardStats() {
        $.ajax({
            url: '/api/dashboard/stats',
            method: 'GET',
            success: function(data) {
                updateStatsCards(data);
                updateAdditionalStats(data);
                loadPortfolioData();
            },
            error: function(xhr) {
                console.error('Error loading dashboard stats:', xhr);
                showAlert('Error loading dashboard data', 'danger');
            }
        });
    }

    function updateStatsCards(data) {
        $('#totalTransactions').text(data.total_transactions.toLocaleString());
        $('#totalInvestment').text(formatCurrency(data.total_investment));
        $('#totalReturns').text(formatCurrency(data.total_returns));
        
        // Update net profit/loss with appropriate styling
        const netProfitLoss = data.net_profit_loss;
        const netProfitElement = $('#netProfitLoss');
        const netProfitIcon = $('#netProfitIcon');
        
        netProfitElement.text(formatCurrency(Math.abs(netProfitLoss)));
        
        if (netProfitLoss > 0) {
            netProfitElement.removeClass('text-danger').addClass('text-success');
            netProfitIcon.removeClass('text-danger').addClass('text-success');
            netProfitElement.prepend('<i class="fas fa-arrow-up me-1"></i>+');
        } else if (netProfitLoss < 0) {
            netProfitElement.removeClass('text-success').addClass('text-danger');
            netProfitIcon.removeClass('text-success').addClass('text-danger');
            netProfitElement.prepend('<i class="fas fa-arrow-down me-1"></i>-');
        } else {
            netProfitElement.removeClass('text-success text-danger');
            netProfitIcon.removeClass('text-success text-danger');
        }
    }

    function updateAdditionalStats(data) {
        $('#activeStocks').text(data.active_stocks.toLocaleString());
        
        // Calculate additional stats from the data
        $.ajax({
            url: '/api/transactions?per_page=-1',
            method: 'GET',
            success: function(transactionData) {
                const transactions = transactionData.transactions;
                
                // Calculate average profit/loss
                let totalProfitLoss = 0;
                let profitableStocks = 0;
                let totalShares = 0;
                let transactionsWithProfitLoss = 0;
                
                transactions.forEach(t => {
                    totalShares += t.remaining_quantity;
                    if (t.profit_loss_percentage !== 0) {
                        totalProfitLoss += t.profit_loss_percentage;
                        transactionsWithProfitLoss++;
                        if (t.profit_loss_percentage > 0) {
                            profitableStocks++;
                        }
                    }
                });
                
                const avgProfitLoss = transactionsWithProfitLoss > 0 ? 
                    totalProfitLoss / transactionsWithProfitLoss : 0;
                
                $('#avgProfitLoss').text(formatPercentage(avgProfitLoss));
                $('#totalShares').text(totalShares.toLocaleString());
                $('#profitableStocks').text(profitableStocks.toLocaleString());
            }
        });
    }


    function loadPortfolioData() {
        $.ajax({
            url: '/api/transactions?per_page=-1',
            method: 'GET',
            success: function(data) {
                createPortfolioChart(data.transactions);
            }
        });
    }

    function createPortfolioChart(transactions) {
        const ctx = document.getElementById('portfolioChart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (portfolioChart) {
            portfolioChart.destroy();
        }

        // Group transactions by stock name and sum remaining quantities
        const portfolioData = {};
        transactions.forEach(t => {
            if (t.remaining_quantity > 0) {
                if (portfolioData[t.stock_name]) {
                    portfolioData[t.stock_name] += t.remaining_quantity;
                } else {
                    portfolioData[t.stock_name] = t.remaining_quantity;
                }
            }
        });

        const stocks = Object.keys(portfolioData);
        if (stocks.length === 0) {
            ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
            ctx.font = '16px Arial';
            ctx.fillStyle = '#6c757d';
            ctx.textAlign = 'center';
            ctx.fillText('No active holdings', ctx.canvas.width / 2, ctx.canvas.height / 2);
            return;
        }

        const quantities = Object.values(portfolioData);
        
        // Generate colors
        const colors = generateColors(stocks.length);
        
        portfolioChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: stocks,
                datasets: [{
                    data: quantities,
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            generateLabels: function(chart) {
                                const data = chart.data;
                                if (data.labels.length && data.datasets.length) {
                                    return data.labels.map((label, i) => {
                                        const dataset = data.datasets[0];
                                        const value = dataset.data[i];
                                        const total = dataset.data.reduce((a, b) => a + b, 0);
                                        const percentage = ((value / total) * 100).toFixed(1);
                                        
                                        return {
                                            text: `${label} (${value} shares - ${percentage}%)`,
                                            fillStyle: dataset.backgroundColor[i],
                                            hidden: false,
                                            index: i
                                        };
                                    });
                                }
                                return [];
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.raw / total) * 100).toFixed(1);
                                return `${context.label}: ${context.raw} shares (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    function generateColors(count) {
        const colors = [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
            '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
        ];
        
        const result = [];
        for (let i = 0; i < count; i++) {
            result.push(colors[i % colors.length]);
        }
        return result;
    }

    // Refresh dashboard every 5 minutes
    setInterval(function() {
        loadDashboardStats();
    }, 300000);
});