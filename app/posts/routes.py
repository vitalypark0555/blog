from flask import Blueprint, render_template, flash, redirect, url_for, abort, request, current_app
from flask_login import current_user, login_required
from app import db

from models import Post, User
from posts.forms import PostForm

posts = Blueprint('posts', __name__)


@posts.route('/post/<int:post_id>')
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post_view.html', title=post.title, post=post)


@posts.route('/user/<username>')
def get_user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    user_posts = Post.query.filter_by(author=user).order_by(Post.id.desc()).paginate(page=page,
                                                                                     per_page=current_app.config[
                                                                                         'PER_PAGE'])
    return render_template('posts.html', title=user.username + "'s Posts", posts=user_posts, user=user)


@posts.route('/post/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.index'))
    return render_template('post_form.html', title='New Post', form=form)


@posts.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
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
        return redirect(url_for('posts.get_post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('post_form.html', title='Update Post', form=form)


@posts.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.index'))
