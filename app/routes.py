from flask import Blueprint, render_template, request, jsonify, make_response, send_file
from app import db
from app.models import StockTransaction
from datetime import datetime
import pandas as pd
import io
import os
from sqlalchemy import func, desc, asc

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# API Routes
@main.route('/api/transactions', methods=['GET'])
def get_transactions():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        query = StockTransaction.query
        
        # Search functionality
        if search:
            query = query.filter(StockTransaction.stock_name.contains(search))
        
        # Sorting
        if hasattr(StockTransaction, sort_by):
            if sort_order == 'desc':
                query = query.order_by(desc(getattr(StockTransaction, sort_by)))
            else:
                query = query.order_by(asc(getattr(StockTransaction, sort_by)))
        
        # Pagination
        if per_page == -1:  # All records
            transactions = query.all()
            total = len(transactions)
            pages = 1
        else:
            paginated = query.paginate(page=page, per_page=per_page, error_out=False)
            transactions = paginated.items
            total = paginated.total
            pages = paginated.pages
        
        return jsonify({
            'transactions': [t.to_dict() for t in transactions],
            'total': total,
            'pages': pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/api/transactions/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    try:
        transaction = StockTransaction.query.get_or_404(transaction_id)
        return jsonify(transaction.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/api/transactions', methods=['POST'])
def create_transaction():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['stock_name', 'buy_quantity', 'buy_price_per_stock', 'buy_date']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Parse date
        try:
            buy_date = datetime.strptime(data['buy_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid buy_date format. Use YYYY-MM-DD'}), 400
        
        sell_date = None
        if data.get('sell_date'):
            try:
                sell_date = datetime.strptime(data['sell_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid sell_date format. Use YYYY-MM-DD'}), 400
        
        transaction = StockTransaction(
            stock_name=data['stock_name'],
            buy_quantity=int(data['buy_quantity']),
            buy_price_per_stock=float(data['buy_price_per_stock']),
            buy_date=buy_date,
            sell_quantity=int(data.get('sell_quantity', 0)),
            sell_price_per_stock=float(data.get('sell_price_per_stock', 0.0)),
            sell_date=sell_date
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify(transaction.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main.route('/api/transactions/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    try:
        transaction = StockTransaction.query.get_or_404(transaction_id)
        data = request.get_json()
        
        # Update fields if provided
        if 'stock_name' in data:
            transaction.stock_name = data['stock_name']
        if 'buy_quantity' in data:
            transaction.buy_quantity = int(data['buy_quantity'])
        if 'buy_price_per_stock' in data:
            transaction.buy_price_per_stock = float(data['buy_price_per_stock'])
        if 'buy_date' in data:
            transaction.buy_date = datetime.strptime(data['buy_date'], '%Y-%m-%d').date()
        if 'sell_quantity' in data:
            transaction.sell_quantity = int(data['sell_quantity'])
        if 'sell_price_per_stock' in data:
            transaction.sell_price_per_stock = float(data['sell_price_per_stock'])
        if 'sell_date' in data and data['sell_date']:
            transaction.sell_date = datetime.strptime(data['sell_date'], '%Y-%m-%d').date()
        elif 'sell_date' in data and not data['sell_date']:
            transaction.sell_date = None
        
        # Recalculate totals
        transaction.calculate_totals()
        
        db.session.commit()
        
        return jsonify(transaction.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    try:
        transaction = StockTransaction.query.get_or_404(transaction_id)
        db.session.delete(transaction)
        db.session.commit()
        
        return jsonify({'message': 'Transaction deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main.route('/api/dashboard/stats')
def dashboard_stats():
    try:
        # Total transactions
        total_transactions = StockTransaction.query.count()
        
        # Total investment (sum of all total_cost)
        total_investment = db.session.query(func.sum(StockTransaction.total_cost)).scalar() or 0.0
        
        # Total returns (sum of all total_selling_cost)
        total_returns = db.session.query(func.sum(StockTransaction.total_selling_cost)).scalar() or 0.0
        
        # Calculate net profit/loss properly
        # For each transaction, calculate the proportional cost of sold stocks and compare with returns
        net_profit_loss = 0.0
        transactions = StockTransaction.query.all()
        
        for t in transactions:
            if t.sell_quantity > 0 and t.total_selling_cost > 0:
                # Calculate the cost of the sold portion
                sold_cost_ratio = float(t.sell_quantity) / float(t.buy_quantity)
                proportional_buy_cost = float(t.total_cost) * sold_cost_ratio
                transaction_profit = float(t.total_selling_cost) - proportional_buy_cost
                net_profit_loss += transaction_profit
        
        # Active stocks (with remaining quantity > 0)
        active_stocks = StockTransaction.query.filter(StockTransaction.remaining_quantity > 0).count()
        
        return jsonify({
            'total_transactions': total_transactions,
            'total_investment': float(total_investment),
            'total_returns': float(total_returns),
            'net_profit_loss': net_profit_loss,
            'active_stocks': active_stocks
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/api/export/csv')
def export_csv():
    try:
        transactions = StockTransaction.query.all()
        
        data = []
        for t in transactions:
            # Calculate holding days
            if t.buy_date:
                end_date = t.sell_date if t.sell_date else datetime.now().date()
                holding_days = (end_date - t.buy_date).days
            else:
                holding_days = 0
                
            data.append({
                'ID': t.id,
                'Stock Name': t.stock_name,
                'Buy Quantity': t.buy_quantity,
                'Buy Price per Stock': float(t.buy_price_per_stock),
                'Total Cost': float(t.total_cost),
                'Buy Date': t.buy_date.isoformat() if t.buy_date else '',
                'Sell Quantity': t.sell_quantity,
                'Sell Price per Stock': float(t.sell_price_per_stock) if t.sell_price_per_stock else 0.0,
                'Total Selling Cost': float(t.total_selling_cost) if t.total_selling_cost else 0.0,
                'Sell Date': t.sell_date.isoformat() if t.sell_date else '',
                'Holding Days': holding_days,
                'Remaining Quantity': t.remaining_quantity,
                'Profit/Loss %': float(t.profit_loss_percentage) if t.profit_loss_percentage else 0.0,
                'Created At': t.created_at.isoformat() if t.created_at else '',
                'Updated At': t.updated_at.isoformat() if t.updated_at else ''
            })
        
        df = pd.DataFrame(data)
        
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=stock_transactions.csv'
        
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/api/export/excel')
def export_excel():
    try:
        transactions = StockTransaction.query.all()
        
        data = []
        for t in transactions:
            # Calculate holding days
            if t.buy_date:
                end_date = t.sell_date if t.sell_date else datetime.now().date()
                holding_days = (end_date - t.buy_date).days
            else:
                holding_days = 0
                
            data.append({
                'ID': t.id,
                'Stock Name': t.stock_name,
                'Buy Quantity': t.buy_quantity,
                'Buy Price per Stock': float(t.buy_price_per_stock),
                'Total Cost': float(t.total_cost),
                'Buy Date': t.buy_date.isoformat() if t.buy_date else '',
                'Sell Quantity': t.sell_quantity,
                'Sell Price per Stock': float(t.sell_price_per_stock) if t.sell_price_per_stock else 0.0,
                'Total Selling Cost': float(t.total_selling_cost) if t.total_selling_cost else 0.0,
                'Sell Date': t.sell_date.isoformat() if t.sell_date else '',
                'Holding Days': holding_days,
                'Remaining Quantity': t.remaining_quantity,
                'Profit/Loss %': float(t.profit_loss_percentage) if t.profit_loss_percentage else 0.0,
                'Created At': t.created_at.isoformat() if t.created_at else '',
                'Updated At': t.updated_at.isoformat() if t.updated_at else ''
            })
        
        df = pd.DataFrame(data)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Stock Transactions')
        
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = 'attachment; filename=stock_transactions.xlsx'
        
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/api/sample-csv')
def download_sample_csv():
    try:
        # Sample data for CSV template
        sample_data = [
            {
                'stock_name': 'RELIANCE',
                'buy_quantity': 10,
                'buy_price_per_stock': 2500.50,
                'buy_date': '2024-01-15',
                'sell_quantity': 5,
                'sell_price_per_stock': 2650.75,
                'sell_date': '2024-02-20'
            },
            {
                'stock_name': 'TCS',
                'buy_quantity': 25,
                'buy_price_per_stock': 3200.00,
                'buy_date': '2024-01-10',
                'sell_quantity': 0,
                'sell_price_per_stock': 0,
                'sell_date': ''
            },
            {
                'stock_name': 'HDFC',
                'buy_quantity': 15,
                'buy_price_per_stock': 1650.25,
                'buy_date': '2024-01-20',
                'sell_quantity': 15,
                'sell_price_per_stock': 1725.50,
                'sell_date': '2024-03-15'
            }
        ]
        
        df = pd.DataFrame(sample_data)
        
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=sample_transactions.csv'
        
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/api/bulk-import', methods=['POST'])
def bulk_import_csv():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.csv'):
            return jsonify({'error': 'File must be a CSV'}), 400
        
        # Read CSV file
        try:
            df = pd.read_csv(file)
        except Exception as e:
            return jsonify({'error': f'Failed to read CSV file: {str(e)}'}), 400
        
        # Validate required columns
        required_columns = ['stock_name', 'buy_quantity', 'buy_price_per_stock', 'buy_date']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return jsonify({'error': f'Missing required columns: {", ".join(missing_columns)}'}), 400
        
        # Process each row
        successful_imports = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Validate required fields
                if pd.isna(row['stock_name']) or not row['stock_name'].strip():
                    errors.append(f'Row {index + 2}: Missing stock name')
                    continue
                
                if pd.isna(row['buy_quantity']) or row['buy_quantity'] <= 0:
                    errors.append(f'Row {index + 2}: Invalid buy quantity')
                    continue
                
                if pd.isna(row['buy_price_per_stock']) or row['buy_price_per_stock'] <= 0:
                    errors.append(f'Row {index + 2}: Invalid buy price')
                    continue
                
                if pd.isna(row['buy_date']):
                    errors.append(f'Row {index + 2}: Missing buy date')
                    continue
                
                # Parse dates
                try:
                    buy_date = datetime.strptime(str(row['buy_date']), '%Y-%m-%d').date()
                except ValueError:
                    try:
                        buy_date = datetime.strptime(str(row['buy_date']), '%m/%d/%Y').date()
                    except ValueError:
                        errors.append(f'Row {index + 2}: Invalid buy date format (use YYYY-MM-DD or MM/DD/YYYY)')
                        continue
                
                sell_date = None
                if 'sell_date' in row and not pd.isna(row['sell_date']) and str(row['sell_date']).strip():
                    try:
                        sell_date = datetime.strptime(str(row['sell_date']), '%Y-%m-%d').date()
                    except ValueError:
                        try:
                            sell_date = datetime.strptime(str(row['sell_date']), '%m/%d/%Y').date()
                        except ValueError:
                            errors.append(f'Row {index + 2}: Invalid sell date format (use YYYY-MM-DD or MM/DD/YYYY)')
                            continue
                
                # Get optional fields
                sell_quantity = int(row.get('sell_quantity', 0)) if not pd.isna(row.get('sell_quantity', 0)) else 0
                sell_price_per_stock = float(row.get('sell_price_per_stock', 0)) if not pd.isna(row.get('sell_price_per_stock', 0)) else 0.0
                
                # Validate sell quantity doesn't exceed buy quantity
                if sell_quantity > row['buy_quantity']:
                    errors.append(f'Row {index + 2}: Sell quantity cannot exceed buy quantity')
                    continue
                
                # Create transaction
                transaction = StockTransaction(
                    stock_name=str(row['stock_name']).strip(),
                    buy_quantity=int(row['buy_quantity']),
                    buy_price_per_stock=float(row['buy_price_per_stock']),
                    buy_date=buy_date,
                    sell_quantity=sell_quantity,
                    sell_price_per_stock=sell_price_per_stock,
                    sell_date=sell_date
                )
                
                db.session.add(transaction)
                successful_imports += 1
                
            except Exception as e:
                errors.append(f'Row {index + 2}: {str(e)}')
                continue
        
        # Commit all transactions
        if successful_imports > 0:
            db.session.commit()
        
        response_data = {
            'message': f'Successfully imported {successful_imports} transactions',
            'successful_imports': successful_imports,
            'total_rows': len(df),
            'errors': errors
        }
        
        if errors:
            response_data['warning'] = f'{len(errors)} rows had errors and were skipped'
        
        return jsonify(response_data), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500