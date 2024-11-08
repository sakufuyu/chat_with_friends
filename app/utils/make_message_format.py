from flask import url_for
from jinja2.utils import urlize

from app.utils.template_filters import replace_newline


def make_message_format(friend, reply):
    message_tag = '<div class="col-lg-1 col-md-1 col-sm-2 col-2">'

    friend_picture_path = f'perm_imgs/{friend}.jpeg'
    message_tag += '<img class="user-image-mini" '
    message_tag += f'src={url_for("static", filename=friend_picture_path)}>'

    message_tag += f'''
        <p>{friend}</p>
        </div>
        <div class="speech-bubble-dest col-lg-4 col-md-8 col-sm-8 col-9">
    '''

    for splited_message in replace_newline(reply):
        message_tag += f'<p>{urlize(splited_message)}</p>'

    message_tag += '''
        </div>
        <div class="col-lg-7 col-md-3 col-sm-1 col-1"></div>
    '''

    return message_tag
