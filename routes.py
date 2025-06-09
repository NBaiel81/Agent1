from flask import Blueprint, render_template, abort, request, redirect, url_for, flash, session, current_app, jsonify, send_from_directory 
from models import Property, db
from werkzeug.utils import secure_filename
import os

main = Blueprint('main', __name__)

# Helper function to delete an image file from static/images
def delete_image_file(filename):
    if not filename:
        return
    image_path = os.path.join(current_app.static_folder, 'images', filename)
    try:
        if os.path.exists(image_path):
            os.remove(image_path)
    except Exception as e:
        current_app.logger.error(f"Error deleting image {filename}: {e}")

@main.route('/')
def index():
    properties = Property.query.all()
    return render_template('index.html', properties=properties)

@main.route('/properties')
def properties():
    properties = Property.query.all()
    return render_template('properties.html', properties=properties)

@main.route('/property/<int:property_id>')
def property_detail(property_id):
    prop = Property.query.get(property_id)
    if not prop:
        abort(404)
    return render_template('details.html', property=prop)

@main.route('/flyer/<int:property_id>')
def flyer(property_id):
    prop = Property.query.get(property_id)
    if not prop:
        abort(404)
    return render_template('flyer.html', property=prop)

# ----- Admin & Authentication -----

@main.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username','')
        password = request.form.get('password','')
        if username == 'Baiel' and password == '12345':
            session['logged_in'] = True
            flash('Logged in successfully', 'success')
            return redirect(url_for('main.admin'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@main.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

def login_required(f):
    from functools import wraps
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in first.', 'warning')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return wrapped

@main.route('/admin')
@login_required
def admin():
    props = Property.query.order_by(Property.id.desc()).all()
    return render_template('admin.html', properties=props)

@main.route('/admin/add', methods=['GET','POST'])
@login_required
def add_property():
    if request.method == 'POST':
        p = Property(
            title       = request.form['title'],
            address     = request.form['address'],
            description = request.form['description'],
            price       = request.form['price'],
            type        = request.form['type'],
            size        = request.form['size'],
            status      = request.form['status'],
            images      = request.form.getlist('images'),
            features    = [line.strip() for line in request.form['features'].splitlines() if line.strip()],
            location    = request.form['location']
        )
        db.session.add(p)
        db.session.commit()
        flash('Property added!', 'success')
        return redirect(url_for('main.admin'))
    return render_template('add_property.html')

@main.route('/admin/edit/<int:property_id>', methods=['GET','POST'])
@login_required
def edit_property(property_id):
    prop = Property.query.get_or_404(property_id)
    if request.method == 'POST':
        existing_images = request.form.getlist('images')
        original_images = prop.images or []
        updated_images = [img for img in existing_images if img.strip()]
        images_to_delete = [img for img in original_images if img not in updated_images]
        for img in images_to_delete:
            delete_image_file(img)
        prop.title       = request.form['title']
        prop.address     = request.form['address']
        prop.description = request.form['description']
        prop.price       = request.form['price']
        prop.type        = request.form['type']
        prop.size        = request.form['size']
        prop.status      = request.form['status']
        prop.images      = updated_images
        prop.features    = [line.strip() for line in request.form['features'].splitlines() if line.strip()]
        prop.location    = request.form['location']
        db.session.commit()
        flash('Property updated!', 'success')
        return redirect(url_for('main.admin'))
    return render_template('edit_property.html', property=prop)

@main.route('/admin/delete/<int:property_id>', methods=['POST'])
@login_required
def delete_property(property_id):
    prop = Property.query.get_or_404(property_id)
    if prop.images:
        for img in prop.images:
            delete_image_file(img)
    db.session.delete(prop)
    db.session.commit()
    flash('Property deleted!', 'info')
    return redirect(url_for('main.admin'))

ALLOWED_EXT = {'png','jpg','jpeg','gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.',1)[1].lower() in ALLOWED_EXT

@main.route('/upload_image', methods=['POST'])
def upload_image():
    file = request.files.get('file')
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400
    fn = secure_filename(file.filename)
    images_dir = os.path.join(current_app.static_folder, 'images')
    os.makedirs(images_dir, exist_ok=True)
    save_path = os.path.join(images_dir, fn)
    base, ext = os.path.splitext(fn)
    i = 1
    while os.path.exists(save_path):
        fn = f"{base}_{i}{ext}"
        save_path = os.path.join(images_dir, fn)
        i += 1
    file.save(save_path)
    return jsonify({'filename': fn})

@main.route('/robots.txt')
def robots_txt():
    return send_from_directory(main.root_path, 'robots.txt')

@main.route('/sitemap.xml')
def sitemap():
    return send_from_directory(main.root_path, 'sitemap.xml')