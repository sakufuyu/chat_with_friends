# views.py

# Native Python libraries
from datetime import datetime
import os
import random
from flask import (
    Blueprint, abort, request, render_template,
    redirect, url_for, flash, jsonify
)
from flask_login import login_user, login_required, logout_user, current_user

# Files in this app
from app.models.models import User, PasswordResetToken, Message
from app.forms.forms import (
    LoginForm, RegisterForm, ResetPasswordForm, ForgotPasswordForm, UserForm,
    ChangePasswordForm, MessageForm
)
from app.utils import make_message_format, user_pictures
from app.bedrock import invoke_model


bp = Blueprint("app", __name__, url_prefix="")


@bp.route("/")
def home():
    friends = ["Robert", "Mikako", "Min-jee", "QUANTUM-X9000"]
    if (current_user.is_authenticated):
        picture_path = current_user.picture_path
        if (picture_path):
            if (not os.path.isfile(picture_path)):
                file = user_pictures.get_picture(picture_path.split("/")[-1])
                picture_path = "app/static/" + picture_path
                open(picture_path, "wb").write(file)

    return render_template("home.html", friends=friends)


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("app.home"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if (request.method == "POST" and form.validate()):
        user = User.get_user_by_email(form.email.data)
        print(form.email.data)
        print(user)
        if (user and user.is_active and user.validate_password(form.password.data)):
            login_user(user, remember=True)
            next = request.args.get("next")
            if not next:
                next = url_for("app.home")
            return redirect(next)
        elif (not user):
            flash("User does not exist")
        elif (not user.is_active):
            flash("This user is inactive. Please reset your password.")
        elif (not user.validate_password(form.password.data)):
            flash("Incorrect email address/password combination.")
    return render_template("login.html", form=form)


@bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if (request.method == "POST" and form.validate()):
        user = User(
            username=form.username.data,
            email=form.email.data
        )

        user.create_new_user()
        token = PasswordResetToken.publish_token(user)

        # Change to send link below bia e-mail
        print(
            f"URL to set password: http://127.0.0.1.5000/reset_password/{token}",
            f"\n Temp pass is: {user.password}"
        )
        flash("Send URL to set password.")
        return redirect(url_for("app.login"))
    return render_template("register.html", form=form)


@bp.route("/reset_password/<uuid:token>", methods=["POST", "GET"])
def reset_password(token):
    form = ResetPasswordForm(request.form)
    reset_user_id = PasswordResetToken.get_user_id_by_token(token)

    if (not reset_user_id):
        abort(500)
    if (request.method == "POST" and form.validate()):
        password = form.password.data
        user = User.get_user_by_id(reset_user_id)

        user.save_new_password(password)
        PasswordResetToken.delete_token(token)

        flash("Password update completed.")
        return redirect(url_for("app.login"))
    return render_template("reset_password.html", form=form)


@bp.route("/forgot_password", methods=["POST", "GET"])
def forgot_password():
    form = ForgotPasswordForm(request.form)
    if (request.method == "POST" and form.validate()):
        email = form.email.data
        user = User.get_user_by_email(email)

        if (user):
            token = PasswordResetToken.publish_token(user)
            reset_url = f"http://127.0.0.1:5000/reset_password/{token}"
            print(reset_url)
            flash("Generate password reset URL")
        else:
            flash("User does not exist.")
    return render_template("forgot_password.html", form=form)


@bp.route("/user", methods=["POST", "GET"])
@login_required
def user():
    form = UserForm(request.form)
    if (request.method == "POST" and form.validate()):
        user_id = current_user.get_id()
        user = User.get_user_by_id(user_id)
        user.username = form.username.data
        user.email = form.email.data
        file = request.files[form.picture_path.name].read()
        if (file):
            file_name = user_id + '_' + \
                str(int(datetime.now().timestamp())) + '.jpg'
            picture_path = "app/static/user_img/" + file_name

            open(picture_path, "wb").write(file)
            user_pictures.save_picture(picture_path, file_name)
            user.picture_path = "user_img/" + file_name

        user.edit_user_info()
        flash("Update user info completed")

    return render_template("user.html", form=form)


@bp.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm(request.form)
    if (request.method == "POST" and form.validate()):
        user = User.get_user_by_id(current_user.id)
        password = form.password.data

        user.save_new_password(password)
        flash("Password updated.")
        return redirect(url_for("app.user"))
    return render_template("change_password.html", form=form)


@bp.route("/message/<friend>", methods=["POST", "GET"])
@login_required
def message(friend):
    """
    ### 🚨🚨🚨
    ### 🚨🚨🚨
    I will set payment status in here to use chatting function with Bedrock.
    ### 🚨🚨🚨
    ### 🚨🚨🚨
    """
    form = MessageForm(request.form)
    user_id = current_user.get_id()
    user = User.get_user_by_id(user_id)
    messages = Message.get_friend_messages(user_id, friend)

    if (request.method == "POST" and form.validate()):
        new_message = form.message.data
        # write message to DB as "user"
        messages.append(
            {'L': [{'S': 'user'}, {'S': new_message}, {"BOOL": False}]}
        )
        Message.record_messages(user_id, friend, messages)
        return redirect(url_for("app.message", friend=friend))

    return render_template(
        "message.html",
        form=form,
        messages=messages,
        friend=friend,
        user_id=user_id,
        user_name=user.username
    )


@bp.route("/message_ajax", methods=["GET"])
@login_required
def message_ajax():
    user_id = request.args.get("user_id", -1, type=str)
    user_name = request.args.get("user_name", "", type=str)
    friend = request.args.get("friend", "")
    messages = Message.get_friend_messages(user_id, friend)

    if (len(messages) > 0):
        if (messages[-1]["L"][0]["S"] == "user"):
            # If your friend already read your message, get replied.
            if (messages[-1]["L"][2]["BOOL"]):
                # Invoke 🛏️🪨 and get reply.
                """
                message_from_friend = invoke_bedrock(friend, messages)
                messages.append({'L': [{'S': 'assistant'}, {'S': message}]})

                record_messages(current_user.get_id(), friend, messages)
                """
                reply = invoke_model.get_friend_message(messages, friend, user_name)
                messages.append({"L": [{"S": "assistant"}, {"S": reply}]})
                Message.record_messages(user_id, friend, messages)

                return jsonify(
                    data=make_message_format.make_message_format(friend, reply),
                    unReadMessagesIdx=[]
                )

            # randomly your friend read your message
            if (random.choice([True, True, False])):
                len_messages = len(messages) - 1
                unread_message_idx = []
                for rev_index, message in enumerate(reversed(messages)):
                    if (message["L"][0]["S"] == "user"):
                        if (message["L"][2]["BOOL"]):
                            break
                        message["L"][2]["BOOL"] = True
                        unread_message_idx.append(len_messages - rev_index)
                Message.record_messages(user_id, friend, messages)

                return jsonify(data="", unReadMessagesIdx=unread_message_idx)

    return jsonify(data="", unReadMessagesIdx=[])


@bp.app_errorhandler(404)
def page_not_found(e):
    return redirect(url_for("app.home"))


@bp.app_errorhandler(500)
def server_error(e):
    error_image_path = "static/perm_imgs/"
    images = [f for f in os.listdir(error_image_path) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    random_image = random.choice(images) if images else None

    return render_template("500.html", random_image=random_image), 500
