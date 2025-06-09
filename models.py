from app import db

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.String(50), nullable=False)
    size = db.Column(db.String(50), nullable=False)       # e.g. "949 SF"
    images = db.Column(db.JSON, nullable=False)           # list of image filenames
    features = db.Column(db.JSON, nullable=False)         # list of feature strings
    location = db.Column(db.String(500), nullable=False)  # Google Maps URL
