# AI Friend Chat Application

This is a Flask-based web application that enables users to chat with AI friends powered by Amazon Bedrock. Users can register, log in, and exchange messages with various AI personalities.

## Test Play Video
[https://d2wm9ivq8if9lh.cloudfront.net/chat_with_friends.html]

## Features

- User authentication (register, login, password reset)
- User profile management (update profile information, change password)
- Chat with AI friends using Amazon Bedrock
- Real-time message updates
- Profile picture upload and management

## Prerequisites

- Python 3.10 or higher
- AWS Account with access to Amazon Bedrock
- AWS CLI configured with appropriate credentials

## AWS Resources Setup

### 1. DynamoDB Tables

Create the following DynamoDB tables:

```bash
# Users table
aws dynamodb create-table \
    --table-name flask_app_users \
    --attribute-definitions \
        AttributeName=id,AttributeType=S \
        AttributeName=email,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --global-secondary-indexes \
        "[{\"IndexName\": \"email-index\",\"KeySchema\":[{\"AttributeName\":\"email\",\"KeyType\":\"HASH\"}],\"Projection\":{\"ProjectionType\":\"ALL\"},\"ProvisionedThroughput\":{\"ReadCapacityUnits\": 5,\"WriteCapacityUnits\": 5}}]" \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

# Password reset tokens table
aws dynamodb create-table \
    --table-name flask_app_password_reset_tokens \
    --attribute-definitions AttributeName=token,AttributeType=S \
    --key-schema AttributeName=token,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

# Messages table (with TTL)
aws dynamodb create-table \
    --table-name messages-records \
    --attribute-definitions \
        AttributeName=id,AttributeType=S \
        AttributeName=friend,AttributeType=S \
    --key-schema \
        AttributeName=id,KeyType=HASH \
        AttributeName=friend,KeyType=RANGE \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

# Enable TTL for messages table
aws dynamodb update-time-to-live \
    --table-name messages-records \
    --time-to-live-specification "Enabled=true, AttributeName=expireAt"
```

### 2. S3 Bucket

Create an S3 bucket for storing user profile pictures:

```bash
aws s3 mb s3://<bucket_name>
```
And replace the bucket name in a python script below:
> app/utils/user_pictures.py

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd sns_app_flask
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # For Unix/MacOS
venv\Scripts\activate     # For Windows
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the root directory with the following variables:
```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=your_region
FLASK_SECRET_KEY=your_flask_secret_key
```

## Running the Application

```bash
python setup.py
```

The application will be available at `http://127.0.0.1:5000`

## Project Structure

- `app/`: Main application package
  - `bedrock/`: Amazon Bedrock integration
  - `forms/`: Form definitions
  - `models/`: Database models
  - `static/`: Static files (CSS, images)
  - `templates/`: HTML templates
  - `utils/`: Utility functions
  - `views/`: Route handlers

## Features Implementation

### User Management
- User registration with email verification
- Password reset functionality
- Profile picture upload and management
- User information updates

### Chat System
- Real-time message updates using AJAX
- Message history with TTL
- AI responses powered by Amazon Bedrock
- Read receipts for messages

## Security Features

- Password hashing using Flask-Bcrypt
- CSRF protection
- Secure file uploads
- Session management
