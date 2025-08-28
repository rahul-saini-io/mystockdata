$(document).ready(function() {
    let transactionsTable;
    let isEditMode = false;
    let currentTransactionId = null;
    let deleteTransactionId = null;

    // Initialize DataTable
    initializeDataTable();

    // Event handlers
    $('#transactionModal').on('show.bs.modal', function() {
        if (!isEditMode) {
            resetForm();
            $('#modalTitle').html('<i class="fas fa-plus-circle me-2"></i>Add Transaction');
        }
    });

    $('#transactionModal').on('hidden.bs.modal', function() {
        resetForm();
        isEditMode = false;
        currentTransactionId = null;
    });

    // Calculate totals on input change
    $('#buyQuantity, #buyPrice').on('input', calculateTotals);
    $('#sellQuantity, #sellPrice').on('input', calculateTotals);

    // Save transaction
    $('#saveTransaction').click(saveTransaction);

    // Confirm delete
    $('#confirmDelete').click(function() {
        if (deleteTransactionId) {
            deleteTransaction(deleteTransactionId);
        }
    });

    // Bulk import handlers
    $('#downloadSampleBtn').click(function(e) {
        e.preventDefault();
        window.location.href = '/api/sample-csv';
    });

    $('#csvFile').on('change', function() {
        const file = this.files[0];
        if (file && file.name.toLowerCase().endsWith('.csv')) {
            $('#uploadCsvBtn').prop('disabled', false);
        } else {
            $('#uploadCsvBtn').prop('disabled', true);
        }
        // Reset results
        $('#importResults').addClass('d-none');
        $('#importSuccess, #importWarning, #importError').hide();
    });

    $('#uploadCsvBtn').click(function() {
        const fileInput = $('#csvFile')[0];
        const file = fileInput.files[0];
        
        if (!file) {
            showAlert('Please select a CSV file first.', 'danger');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        // Disable button and show loading
        $('#uploadCsvBtn').prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-1"></i>Uploading...');

        $.ajax({
            url: '/api/bulk-import',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                $('#importResults').removeClass('d-none');
                
                if (response.errors && response.errors.length > 0) {
                    // Show warning with errors
                    $('#importWarning').show();
                    $('#warningMessage').text(response.message);
                    
                    const errorList = $('#errorList');
                    errorList.empty();
                    response.errors.forEach(function(error) {
                        errorList.append(`<li>${error}</li>`);
                    });
                    
                    if (response.warning) {
                        $('#warningMessage').text(response.warning + '. ' + response.message);
                    }
                } else {
                    // Show success
                    $('#importSuccess').show();
                    $('#successMessage').text(response.message);
                }

                // Reload the data table
                transactionsTable.ajax.reload();
                
                // Reset form
                $('#csvFile').val('');
                
                // Auto close modal after 3 seconds for successful imports
                if (!response.errors || response.errors.length === 0) {
                    setTimeout(function() {
                        $('#bulkImportModal').modal('hide');
                    }, 3000);
                }
            },
            error: function(xhr) {
                $('#importResults').removeClass('d-none');
                $('#importError').show();
                
                const error = xhr.responseJSON ? xhr.responseJSON.error : 'Upload failed';
                $('#errorMessage').text(error);
            },
            complete: function() {
                // Re-enable button
                $('#uploadCsvBtn').prop('disabled', false).html('<i class="fas fa-upload me-1"></i>Upload CSV');
            }
        });
    });

    // Reset bulk import modal when closed
    $('#bulkImportModal').on('hidden.bs.modal', function() {
        $('#csvFile').val('');
        $('#uploadCsvBtn').prop('disabled', true);
        $('#importResults').addClass('d-none');
        $('#importSuccess, #importWarning, #importError').hide();
    });

    // Functions
    function initializeDataTable() {
        transactionsTable = $('#transactionsTable').DataTable({
            processing: true,
            serverSide: false,
            ajax: {
                url: '/api/transactions',
                data: function(d) {
                    d.per_page = -1; // Get all records for client-side processing
                },
                dataSrc: 'transactions'
            },
            columns: [
                { 
                    data: 'stock_name',
                    render: function(data, type, row) {
                        return `<strong>${data}</strong>`;
                    }
                },
                { data: 'buy_quantity' },
                { 
                    data: 'buy_price_per_stock',
                    render: function(data, type, row) {
                        return formatCurrency(data);
                    }
                },
                { 
                    data: 'total_cost',
                    render: function(data, type, row) {
                        return formatCurrency(data);
                    }
                },
                { 
                    data: 'buy_date',
                    render: function(data, type, row) {
                        return data ? new Date(data).toLocaleDateString() : '-';
                    }
                },
                { data: 'sell_quantity' },
                { 
                    data: 'sell_price_per_stock',
                    render: function(data, type, row) {
                        return data > 0 ? formatCurrency(data) : '-';
                    }
                },
                { 
                    data: 'total_selling_cost',
                    render: function(data, type, row) {
                        return data > 0 ? formatCurrency(data) : '-';
                    }
                },
                { 
                    data: 'sell_date',
                    render: function(data, type, row) {
                        return data ? new Date(data).toLocaleDateString() : '-';
                    }
                },
                { 
                    data: null,
                    render: function(data, type, row) {
                        if (!row.buy_date) return '<span class="badge bg-secondary">0 days</span>';
                        
                        const buyDate = new Date(row.buy_date);
                        let endDate;
                        let badgeClass;
                        
                        if (row.sell_date) {
                            // Stock has been sold - use sell date as end date
                            endDate = new Date(row.sell_date);
                            badgeClass = 'bg-secondary';
                        } else {
                            // Stock is still held - use current date
                            endDate = new Date();
                            badgeClass = 'bg-primary';
                        }
                        
                        const diffTime = Math.abs(endDate - buyDate);
                        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                        
                        return `<span class="badge ${badgeClass}">${diffDays} days</span>`;
                    }
                },
                { 
                    data: 'remaining_quantity',
                    render: function(data, type, row) {
                        return `<span class="badge bg-${data > 0 ? 'success' : 'secondary'}">${data}</span>`;
                    }
                },
                { 
                    data: 'profit_loss_percentage',
                    render: function(data, type, row) {
                        const className = data > 0 ? 'profit' : data < 0 ? 'loss' : '';
                        const icon = data > 0 ? 'fas fa-arrow-up' : data < 0 ? 'fas fa-arrow-down' : 'fas fa-minus';
                        return `<span class="${className}"><i class="${icon} me-1"></i>${formatPercentage(data)}</span>`;
                    }
                },
                {
                    data: null,
                    orderable: false,
                    render: function(data, type, row) {
                        return `
                            <div class="btn-group btn-group-sm">
                                <button class="btn btn-outline-primary btn-edit" data-id="${row.id}" title="Edit">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-outline-danger btn-delete" data-id="${row.id}" 
                                        data-stock="${row.stock_name}" data-qty="${row.buy_quantity}" title="Delete">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        `;
                    }
                }
            ],
            order: [[4, 'desc']], // Sort by buy_date descending
            responsive: true,
            pageLength: 25,
            language: {
                processing: '<i class="fas fa-spinner fa-spin"></i> Loading...'
            }
        });

        // Handle edit button click
        $('#transactionsTable tbody').on('click', '.btn-edit', function() {
            const transactionId = $(this).data('id');
            editTransaction(transactionId);
        });

        // Handle delete button click
        $('#transactionsTable tbody').on('click', '.btn-delete', function() {
            deleteTransactionId = $(this).data('id');
            $('#deleteStockName').text($(this).data('stock'));
            $('#deleteQuantity').text($(this).data('qty') + ' shares');
            $('#deleteModal').modal('show');
        });
    }

    function calculateTotals() {
        const buyQty = parseInt($('#buyQuantity').val()) || 0;
        const buyPrice = parseFloat($('#buyPrice').val()) || 0;
        const sellQty = parseInt($('#sellQuantity').val()) || 0;
        const sellPrice = parseFloat($('#sellPrice').val()) || 0;

        // Calculate total cost
        const totalCost = buyQty * buyPrice;
        $('#totalCost').text(formatCurrency(totalCost));

        // Calculate total selling cost
        const totalSellingCost = sellQty * sellPrice;
        $('#totalSellingCost').text(formatCurrency(totalSellingCost));

        // Calculate remaining quantity
        const remaining = buyQty - sellQty;
        $('#remainingQuantity').text(remaining);

        // Validate sell quantity
        if (sellQty > buyQty) {
            $('#sellQuantity').addClass('is-invalid');
        } else {
            $('#sellQuantity').removeClass('is-invalid');
        }
    }

    function resetForm() {
        $('#transactionForm')[0].reset();
        $('#transactionId').val('');
        $('#totalCost').text('₹0.00');
        $('#totalSellingCost').text('₹0.00');
        $('#remainingQuantity').text('0');
        $('.form-control').removeClass('is-invalid');
        
        // Set today's date as default for buy date
        const today = new Date().toISOString().split('T')[0];
        $('#buyDate').val(today);
    }

    function saveTransaction() {
        const formData = {
            stock_name: $('#stockName').val(),
            buy_quantity: parseInt($('#buyQuantity').val()),
            buy_price_per_stock: parseFloat($('#buyPrice').val()),
            buy_date: $('#buyDate').val(),
            sell_quantity: parseInt($('#sellQuantity').val()) || 0,
            sell_price_per_stock: parseFloat($('#sellPrice').val()) || 0.0,
            sell_date: $('#sellDate').val() || null
        };

        // Validation
        if (!formData.stock_name || !formData.buy_quantity || !formData.buy_price_per_stock || !formData.buy_date) {
            showAlert('Please fill in all required fields.', 'danger');
            return;
        }

        if (formData.sell_quantity > formData.buy_quantity) {
            showAlert('Sell quantity cannot exceed buy quantity.', 'danger');
            return;
        }

        const url = isEditMode ? `/api/transactions/${currentTransactionId}` : '/api/transactions';
        const method = isEditMode ? 'PUT' : 'POST';

        $.ajax({
            url: url,
            method: method,
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response) {
                showAlert(`Transaction ${isEditMode ? 'updated' : 'added'} successfully!`);
                $('#transactionModal').modal('hide');
                transactionsTable.ajax.reload();
            },
            error: function(xhr) {
                const error = xhr.responseJSON ? xhr.responseJSON.error : 'An error occurred';
                showAlert(error, 'danger');
            }
        });
    }

    function editTransaction(transactionId) {
        $.ajax({
            url: `/api/transactions/${transactionId}`,
            method: 'GET',
            success: function(transaction) {
                isEditMode = true;
                currentTransactionId = transactionId;

                // Populate form
                $('#transactionId').val(transaction.id);
                $('#stockName').val(transaction.stock_name);
                $('#buyQuantity').val(transaction.buy_quantity);
                $('#buyPrice').val(transaction.buy_price_per_stock);
                $('#buyDate').val(transaction.buy_date);
                $('#sellQuantity').val(transaction.sell_quantity || '');
                $('#sellPrice').val(transaction.sell_price_per_stock || '');
                $('#sellDate').val(transaction.sell_date || '');

                calculateTotals();

                $('#modalTitle').html('<i class="fas fa-edit me-2"></i>Edit Transaction');
                $('#transactionModal').modal('show');
            },
            error: function(xhr) {
                const error = xhr.responseJSON ? xhr.responseJSON.error : 'An error occurred';
                showAlert(error, 'danger');
            }
        });
    }

    function deleteTransaction(transactionId) {
        $.ajax({
            url: `/api/transactions/${transactionId}`,
            method: 'DELETE',
            success: function(response) {
                showAlert('Transaction deleted successfully!');
                $('#deleteModal').modal('hide');
                transactionsTable.ajax.reload();
                deleteTransactionId = null;
            },
            error: function(xhr) {
                const error = xhr.responseJSON ? xhr.responseJSON.error : 'An error occurred';
                showAlert(error, 'danger');
            }
        });
    }
});