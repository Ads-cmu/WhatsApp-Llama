import re
import json
import sys

def remove_placeholders(message):
    skip_list = ['<This message was edited>', 'This message was deleted.', ' omitted\n']
    return any(phrase in message for phrase in skip_list)

def replace_users(message, contact_name, friend_name, bot_name, your_contact_name):
    message = re.sub(your_contact_name, bot_name, message)
    message = re.sub(contact_name, friend_name, message)
    return message

def remove_links(message):
    return re.sub(r"http\S*", '', message)

def get_user_text(message):
    if ': ' not in message:
        return None, message
    try:
        user, text = message.split(": ", 1)
    except Exception as e:
        print("Error while splitting message:", e)
        print("Original message:", message)
        return message.split(":")[0], ''
    return user, text

def collate_messages(messages, user_name, bot_name, friend_name):
    conversations = []
    current_message = {"user": None, "text": ""}

    for message in messages:
        user, text = get_user_text(message)

        if current_message["user"] is None:
            current_message["user"] = user

        if user != current_message["user"]:
            if current_message["user"] == user_name:
                conversations.append({'Friend (' + friend_name + ')': current_message["text"]})
            else:
                conversations.append({current_message["user"]: current_message["text"]})

            current_message["user"] = user
            current_message["text"] = text
        else:
            current_message["text"] += " " + text

    # To capture the last message
    if current_message["user"]:
        if current_message["user"] == user_name:
            conversations.append({'Friend (' + friend_name + ')': current_message["text"]})
        else:
            conversations.append({current_message["user"]: current_message["text"]})

    return conversations

if __name__ == "__main__":
    if len(sys.argv) != 7:
        print("Usage: preprocessing.py <your_name> <your_contact_name> <friend_name> <friend_contact_name> <input_folder_path> <output_folder_path>")
        sys.exit(1)

    bot_name = sys.argv[1]
    your_contact_name = sys.argv[2]
    friend_name = sys.argv[3]
    contact_name = sys.argv[4]
    input_folder_path = sys.argv[5]
    output_folder_path = sys.argv[6]

    with open(input_folder_path + '/' + friend_name + 'Chat.txt', encoding="utf-8") as f:
        lines = f.readlines()

    regex = r"\s?\[\d{1,2}\/\d{1,2}\/\d{2,4}\, \d{1,2}:\d{1,2}:\d{1,2}\s[APM]{2}\]\s"  # to identify timestamps

    messages = []
    message_buffer = ''
    for line in lines:
        if re.match(regex, line):
            if message_buffer:
                messages.append(message_buffer)
                message_buffer = ''
            message_buffer = re.sub(regex, "", line)
        else:
            message_buffer += line

    if message_buffer:  # To capture the last message
        messages.append(message_buffer)

    dataset = []

    for message in messages:
        if remove_placeholders(message):
            continue
        message = remove_links(message)
        message = replace_users(message, contact_name, friend_name, bot_name, your_contact_name)
        dataset.append(message)

    dataset = collate_messages(dataset, friend_name, bot_name, friend_name)

    with open(output_folder_path + '/' + friend_name + 'Chat.json', 'w') as file:
        json.dump(dataset, file, indent=4)

