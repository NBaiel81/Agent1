from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import urllib.parse
import re

db = SQLAlchemy()

def create_app():
    app = Flask(
        __name__,
        static_folder='static',
        template_folder='templates'
    )
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///properties.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Custom filter to convert Google Maps URL to embed URL
    @app.template_filter('to_embed_url')
    def to_embed_url(url):
        if not url:
            return url

        # If it's already an embed URL, return it as is
        if '/embed?pb' in url:
            return url

        # If it's a place URL, convert it to embed URL
        if '/place/' in url:
            # Parse the URL
            parsed_url = urllib.parse.urlparse(url)
            path = parsed_url.path
            query = urllib.parse.parse_qs(parsed_url.query)

            # Extract the address from the path
            address_part = path.split('/place/')[1].split('/@')[0]
            address = urllib.parse.unquote(address_part)

            # Extract coordinates from the path (e.g., @49.9053901,-97.1048772,17z)
            coords_match = re.search(r'@([\d.-]+),([\d.-]+),(\d+)z', path)
            lat, lng, zoom = 49.9053901, -97.1048772, 17  # Fallback values
            if coords_match:
                lat, lng, zoom = map(float, coords_match.groups())

            # Extract place ID from data parameter (e.g., 1s0x52ea711f97a28d4d:0xb3cde497c0095f62)
            place_id_match = re.search(r'1s(0x[a-f0-9]+:[a-f0-9]+)', url)
            place_id = '0x0:0x0'  # Fallback
            if place_id_match:
                place_id = place_id_match.group(1)

            # Construct the embed URL
            embed_url = (
                f"https://www.google.com/maps/embed?pb="
                f"!1m18!1m12!1m3!1d{2847.938850338206 if not coords_match else (2 ** (21 - int(zoom)) * 1000)}"
                f"!2d{lng}!3d{lat}!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2"
                f"!1s{place_id}!2s{urllib.parse.quote(address)}!5e0!3m2!1sen!2sca!4v1713468540000!5m2!1sen!2sca"
            )
            return embed_url

        # If the URL format is unrecognized, return a fallback embed URL or the original URL
        return url

    with app.app_context():
        # Import models so that they are registered with SQLAlchemy
        from models import Property
        db.create_all()

        # Register routes
        from routes import main
        app.register_blueprint(main)

    return app

app = create_app()