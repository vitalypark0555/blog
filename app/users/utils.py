import os
import secrets

from PIL import Image
from flask_mail import Message
from flask import url_for, current_app


def save_image(form_image):
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(form_image.filename)
    image_fn = random_hex + file_ext
    image_path = os.path.join(current_app.root_path, 'static/profile_images', image_fn)

    image = Image.open(form_image)
    output_size = (125, 125)
    image.thumbnail(output_size)
    image.save(image_path)

    return image_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender=os.environ.get('EMAIL_USERNAME'), recipients=[user.email])
    msg.body = f'''To reset your password visit the following link:
    {url_for('users.reset_token', token=token, _external=True)}
    If you did not make this request then please ignore this email and no changes will be made.
    '''
    current_app.mail.send(msg)
