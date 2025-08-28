from app import create_app, db
from app.models import StockTransaction

app = create_app('development')

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'StockTransaction': StockTransaction}

@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    print("Database tables created successfully!")

@app.cli.command()
def seed_db():
    """Seed the database with sample data."""
    from datetime import date, timedelta
    import random
    
    # Sample stock data
    stocks = [
        {'name': 'Apple Inc.', 'symbol': 'AAPL'},
        {'name': 'Microsoft Corporation', 'symbol': 'MSFT'},
        {'name': 'Amazon.com Inc.', 'symbol': 'AMZN'},
        {'name': 'Alphabet Inc.', 'symbol': 'GOOGL'},
        {'name': 'Tesla Inc.', 'symbol': 'TSLA'}
    ]
    
    # Clear existing data
    StockTransaction.query.delete()
    
    # Create sample transactions
    for i, stock in enumerate(stocks):
        # Create multiple transactions for each stock
        for j in range(random.randint(1, 3)):
            buy_date = date.today() - timedelta(days=random.randint(30, 365))
            buy_quantity = random.randint(10, 100)
            buy_price = random.uniform(50, 500)
            
            # Randomly decide if stock is sold
            is_sold = random.choice([True, False, False])  # 33% chance of being sold
            
            sell_quantity = 0
            sell_price = 0.0
            sell_date = None
            
            if is_sold:
                sell_quantity = random.randint(1, buy_quantity)
                # Simulate profit/loss with 60% chance of profit
                price_change = random.uniform(-0.3, 0.5) if random.random() > 0.4 else random.uniform(-0.1, 0.3)
                sell_price = buy_price * (1 + price_change)
                sell_date = buy_date + timedelta(days=random.randint(1, 200))
            
            transaction = StockTransaction(
                stock_name=stock['name'],
                buy_quantity=buy_quantity,
                buy_price_per_stock=round(buy_price, 2),
                buy_date=buy_date,
                sell_quantity=sell_quantity,
                sell_price_per_stock=round(sell_price, 2) if sell_price > 0 else 0.0,
                sell_date=sell_date
            )
            
            db.session.add(transaction)
    
    db.session.commit()
    print(f"Database seeded with {len(stocks) * 2} sample transactions!")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)