from datetime import datetime
from app import db, login_manager, app
from flask_login import UserMixin
from marshmallow import Schema, fields
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader
def get_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', back_populates='posts')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', back_populates='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except Exception as e:
            print(e)
            return None
        return User.query.get(user_id)


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.String()
    image = fields.String()


class PostSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.String()
    content = fields.String()
    author = fields.Nested(UserSchema)
    created_at = fields.Date(dump_only=True)
