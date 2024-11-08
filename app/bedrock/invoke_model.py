import boto3
import os

bedrock = boto3.client("bedrock-runtime")
model_id = "us.anthropic.claude-3-5-sonnet-20240620-v1:0"
current_dir = os.path.dirname(__file__)


def get_friend(friend, user_name):
    file_path = os.path.join(current_dir, "friends", f"{friend}.txt")
    with open(file_path, "r") as f:
        system_prompt = f.read()
    system_prompt += f"""
    <important>
    NEVER SAY you are an AI. 
    You need to behave as the profile introduced yourself as above.
    This is a message chat exchange between you and the user.
    You are user's friend.
    Also, user name is {user_name}
    </important>
    """

    return system_prompt


def get_friend_message(message_records, friend, user_name):
    system_prompt = get_friend(friend, user_name)
    messages = list()

    prev_role = ""
    for message_record in message_records:
        role = message_record["L"][0]["S"]
        message = message_record["L"][1]["S"]

        if (role == "user"):
            if (prev_role == "user"):
                messages[-1]["content"][0]["text"] += message
                continue
        messages.append({"role": role, "content": [{"text": message}]})
        prev_role = role

    response = bedrock.converse(
        modelId=model_id,
        system=[
            {
                "text": system_prompt
            }
        ],
        messages=messages,
        inferenceConfig={"maxTokens": 390, "temperature": 1.0, "topP": 0.9}
    )

    return response["output"]["message"]["content"][0]["text"]
