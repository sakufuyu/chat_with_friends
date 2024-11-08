# models.py
from flask import current_app
from flask_login import UserMixin
from datetime import datetime, timedelta
from uuid import uuid4
from botocore.exceptions import ClientError
from app.utils.password import (
    generate_temp_password, hashing_password, confirm_password
)

from app import login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.get_user_by_id(user_id)


class User(UserMixin):
    table_name = "flask_app_users"

    def __init__(self, username, email, id=str(uuid4()), password=generate_temp_password(15), picture_path="", is_active=False, create_at="", update_at=""):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.picture_path = picture_path
        self.is_active = is_active
        self.create_at = create_at
        self.update_at = update_at

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, value):
        self._is_active = value

    @classmethod
    def get_user_by_email(cls, email):
        try:
            response = current_app.dynamodb.query(
                TableName=cls.table_name,
                IndexName="email-index",
                KeyConditionExpression="email = :email_val",
                ExpressionAttributeValues={
                    ":email_val": {"S": email}
                },
                ProjectionExpression="id"
            )
            email_item = response.get("Items")
            if (email_item):
                user_id = email_item[0]["id"]["S"]
                return cls.get_user_by_id(user_id)
        except ClientError as e:
            print("Error in get_user_by_email:", e.response["Error"]["Message"])
        return None

    @classmethod
    def get_user_by_id(cls, id):
        try:
            response = current_app.dynamodb.get_item(
                TableName=cls.table_name,
                Key={"id": {"S": id}}
            )
            item = response.get("Item")
            if item:
                return cls(
                    id=item.get("id", {}).get("S"),
                    username=item.get("username", {}).get("S"),
                    email=item.get("email", {}).get("S"),
                    password=item.get("password", {}).get("S"),
                    picture_path=item.get("picture_path", {}).get("S", ""),
                    is_active=item.get("is_active", {}).get("BOOL", False),
                    create_at=item.get("create_at", {}).get("S", ""),
                    update_at=item.get("update_at", {}).get("S", "")
                )
        except ClientError as e:
            print(e.response["Error"]["Message"])
            return None

    def validate_password(self, password):
        return confirm_password(self.password, password)

    def create_new_user(self):
        try:
            current_app.dynamodb.put_item(
                TableName="flask_app_users",
                Item={
                    "id": {"S": self.id},
                    "username": {"S": self.username},
                    "email": {"S": self.email},
                    "password": {"S": hashing_password(self.password)},
                    "is_active": {"BOOL": False},
                    "create_at": {"S": datetime.now().isoformat()},
                    "update_at": {"S": datetime.now().isoformat()}
                }
            )
        except ClientError as e:
            print(e.response["Error"]["Message"])
            raise e

    def save_new_password(self, new_password):
        try:
            current_app.dynamodb.update_item(
                TableName="flask_app_users",
                Key={"id": {"S": str(self.id)}},
                UpdateExpression="SET password = :p, is_active = :a, update_at = :u",
                ExpressionAttributeValues={
                    ":p": {"S": hashing_password(new_password)},
                    ":a": {"BOOL": True},
                    ":u": {"S": datetime.now().isoformat()}
                }
            )
        except ClientError as e:
            print(e.response["Error"]["Message"])

    def edit_user_info(self):
        try:
            current_app.dynamodb.update_item(
                TableName="flask_app_users",
                Key={"id": {"S": str(self.id)}},
                UpdateExpression="SET username = :un, email = :e, picture_path = :p, update_at = :ua",
                ExpressionAttributeValues={
                    ":un": {"S": self.username},
                    ":e": {"S": self.email},
                    ":p": {"S": self.picture_path},
                    ":ua": {"S": datetime.now().isoformat()}
                }
            )
        except ClientError as e:
            print(e.response["Error"]["Message"])


class PasswordResetToken:
    table_name = "flask_app_password_reset_tokens"

    @classmethod
    def publish_token(cls, user):
        token = str(uuid4())
        expire_at = (datetime.now() + timedelta(hours=1)).isoformat()
        try:
            current_app.dynamodb.put_item(
                TableName=cls.table_name,
                Item={
                    "token": {"S": token},
                    "user_id": {"S": user.id},
                    "expire_at": {"S": expire_at},
                    "create_at": {"S": datetime.now().isoformat()}
                }
            )
        except ClientError as e:
            print(e.response["Error"]["Message"])
        return token

    @classmethod
    def get_user_id_by_token(cls, token):
        try:
            token = str(token)
            response = current_app.dynamodb.get_item(
                TableName=cls.table_name,
                Key={"token": {"S": token}}
            )
            item = response.get("Item")
            if (item):
                expire_at = datetime.strptime(item["expire_at"]["S"], "%Y-%m-%dT%H:%M:%S.%f")
                if (expire_at > datetime.now()):
                    return item["user_id"]["S"]
            else:
                return None
        except ClientError as e:
            print(e.response["Error"]["Message"])
        return None

    @classmethod
    def delete_token(cls, token):
        token = str(token)
        try:
            current_app.dynamodb.delete_item(
                TableName=cls.table_name,
                Key={"token": {"S": token}}
            )
        except ClientError as e:
            print(e.response["Error"]["Message"])


class Message:
    table_name = "messages-records"

    def __init__(self, id, friend, messages):
        self.id = id
        self.friend = friend
        self.messages = messages

    @classmethod
    def get_friend_messages(cls, id, friend):
        # get messages records from ddb
        # or create new item
        try:
            response = current_app.dynamodb.get_item(
                TableName=cls.table_name,
                Key={"id": {"S": id}, "friend": {"S": friend}}
            )
            item = response.get("Item")

            if (item):
                # Ex.
                # messages: 
                #  [{'L': [{'S': 'user'}, {'S': 'Hello'}]}, {'L': [{'S': 'assistant'}, {'S': 'Hi! How are you!'}]}]
                messages = item["messages"]["L"]

                return messages
            else:
                response = current_app.dynamodb.put_item(
                    TableName=cls.table_name,
                    Item={
                        "id": {"S": id},
                        "friend": {"S": friend},
                        "messages": {"L": []}
                    }
                )
                return []
        except ClientError as e:
            print(e.response["Error"]["Message"])

    @classmethod
    def record_messages(cls, id, friend, messages):
        try:
            # Set TTL to DDB table. Session time is 1H after last message.
            expire_at = int((datetime.now() + timedelta(hours=1)).timestamp())

            current_app.dynamodb.update_item(
                TableName=cls.table_name,
                Key={
                    "id": {"S": id},
                    "friend": {"S": friend}
                },
                UpdateExpression="SET messages = :m, expireAt = :e",
                ExpressionAttributeValues={
                    ":m": {"L": messages},
                    ":e": {"N": str(expire_at)}
                },
                ReturnValues="UPDATED_NEW"
            )
        except ClientError as e:
            print(e.response["Error"]["Message"])
