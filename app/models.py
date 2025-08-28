from app import db
from datetime import datetime
from sqlalchemy import event

class StockTransaction(db.Model):
    __tablename__ = 'stock_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_name = db.Column(db.String(100), nullable=False, index=True)
    
    # Buy data
    buy_quantity = db.Column(db.Integer, nullable=False)
    buy_price_per_stock = db.Column(db.Numeric(10, 4), nullable=False)
    total_cost = db.Column(db.Numeric(15, 4), nullable=False)
    buy_date = db.Column(db.Date, nullable=False, index=True)
    
    # Sell data (nullable as stocks might not be sold yet)
    sell_quantity = db.Column(db.Integer, nullable=True, default=0)
    sell_price_per_stock = db.Column(db.Numeric(10, 4), nullable=True, default=0.0)
    total_selling_cost = db.Column(db.Numeric(15, 4), nullable=True, default=0.0)
    sell_date = db.Column(db.Date, nullable=True)
    
    # Calculated fields
    remaining_quantity = db.Column(db.Integer, nullable=False)
    profit_loss_percentage = db.Column(db.Numeric(10, 4), nullable=True, default=0.0)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(StockTransaction, self).__init__(**kwargs)
        self.calculate_totals()
    
    def calculate_totals(self):
        # Calculate total cost
        if self.buy_quantity and self.buy_price_per_stock:
            self.total_cost = float(self.buy_quantity) * float(self.buy_price_per_stock)
        
        # Calculate total selling cost
        if self.sell_quantity and self.sell_price_per_stock:
            self.total_selling_cost = float(self.sell_quantity) * float(self.sell_price_per_stock)
        else:
            self.sell_quantity = self.sell_quantity or 0
            self.sell_price_per_stock = self.sell_price_per_stock or 0.0
            self.total_selling_cost = 0.0
        
        # Calculate remaining quantity
        self.remaining_quantity = self.buy_quantity - (self.sell_quantity or 0)
        
        # Calculate profit/loss percentage
        if self.total_selling_cost and self.total_cost and self.total_cost > 0:
            sold_cost_ratio = float(self.sell_quantity) / float(self.buy_quantity)
            proportional_buy_cost = float(self.total_cost) * sold_cost_ratio
            self.profit_loss_percentage = ((float(self.total_selling_cost) - proportional_buy_cost) / proportional_buy_cost) * 100
        else:
            self.profit_loss_percentage = 0.0
    
    def to_dict(self):
        return {
            'id': self.id,
            'stock_name': self.stock_name,
            'buy_quantity': self.buy_quantity,
            'buy_price_per_stock': float(self.buy_price_per_stock),
            'total_cost': float(self.total_cost),
            'buy_date': self.buy_date.isoformat() if self.buy_date else None,
            'sell_quantity': self.sell_quantity,
            'sell_price_per_stock': float(self.sell_price_per_stock) if self.sell_price_per_stock else 0.0,
            'total_selling_cost': float(self.total_selling_cost) if self.total_selling_cost else 0.0,
            'sell_date': self.sell_date.isoformat() if self.sell_date else None,
            'remaining_quantity': self.remaining_quantity,
            'profit_loss_percentage': float(self.profit_loss_percentage) if self.profit_loss_percentage else 0.0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<StockTransaction {self.stock_name}: {self.buy_quantity} shares>'

# Event listener to recalculate totals when the model is updated
@event.listens_for(StockTransaction, 'before_update')
def recalculate_totals(mapper, connection, target):
    target.calculate_totals()