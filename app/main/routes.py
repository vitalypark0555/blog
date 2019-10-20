from flask import Blueprint, request, render_template, jsonify, current_app

from models import Post, PostSchema

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def index():
    posts = []
    if request.method == 'GET':
        posts = Post.query.order_by(Post.id.desc()).limit(current_app.config['PER_PAGE'])
        return render_template('index.html', posts=posts)
    else:
        last_post_id = request.form.get('last_post_id')
        post_schema = PostSchema(many=True)
        posts = Post.query.filter(Post.id < last_post_id).order_by(Post.id.desc()).limit(current_app.config['PER_PAGE'])
        return jsonify(post_schema.dump(posts))


@main.route('/about')
def about():
    return render_template('about.html', title='About')
