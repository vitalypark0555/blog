import os
import secrets
from PIL import Image
from flask import flash, redirect, url_for, request, abort
from flask import render_template, jsonify
from app.forms import RegistrationForm, LoginForm, UpdateProfileForm, PostForm
from app import app, db, bcrypt
from app.models import User, Post, PostSchema
from flask_login import login_user, current_user, logout_user, login_required


@app.route('/', methods=['GET', 'POST'])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    posts = []
    if request.method == 'GET':
        posts = Post.query.order_by(Post.id.desc()).limit(10)
        return render_template('index.html', posts=posts)
    else:
        last_post_id = request.form.get('last_post_id')
        post_schema = PostSchema(many=True)
        posts = Post.query.filter(Post.id < last_post_id).order_by(Post.id.desc()).limit(10)
        return jsonify(post_schema.dump(posts))


@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('You have been successfully registered! Log into your account.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Sign up', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        flash('Login failed. Invalid username or password.', 'danger')
    return render_template('login.html', title='Sign in', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


def save_image(form_image):
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(form_image.filename)
    image_fn = random_hex + file_ext
    image_path = os.path.join(app.root_path, 'static/profile_images', image_fn)

    image = Image.open(form_image)
    output_size = (125, 125)
    image.thumbnail(output_size)
    image.save(image_path)

    return image_fn


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.image.data:
            image_file = save_image(form.image.data)
            current_user.image = image_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your profile has been updated.', 'info')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image = url_for('static', filename='profile_images/' + current_user.image)
    return render_template('profile.html', title='Profile', image=image, form=form)


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('index'))
    return render_template('post_form.html', title='New Post', legend='New Post', form=form)


@app.route('/post/<int:post_id>')
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post_view.html', title=post.title, post=post)


@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'info')
        return redirect(url_for('get_post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('post_form.html', title='Update Post', legend='Update Post', form=form)


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('index'))
