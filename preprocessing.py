import re
import json
import os 
import sys

def remove_placeholders(message):
	skip_list = ['<This message was edited>','This message was deleted.',' omitted\n']
	for phrase in skip_list:
		if phrase in message:
			return True
	return False

def replace_users(message, contact_name, friend_name,bot_name, your_contact_name):
	message = re.sub(your_contact_name, bot_name, message)
	message = re.sub(contact_name, friend_name, message)
	return message

def remove_links(message):
	message = re.sub(r"http\S*", '', message)
	return message

def get_user_text(message):
	if ': ' not in message:
		return None,message
	try:
		user, text = message.split(": ", 1)
	except Exception as e:
		print(e)
		print(message)
		return message.split(":")[0],''
	return user, text

def clean_text(text):
	return text.split(":")[0]

def collate_messages(messages, user_name, bot_name, friend_name):
	conversations = []

	fp = 0
	sp = 0
	snippet = ''

	while sp < len(messages):
		if snippet =='':
			og_user,_ = get_user_text(messages[fp])
		cur_user,text = get_user_text(messages[sp])
		if cur_user==og_user or cur_user==None:
			snippet = snippet + clean_text(text)
			sp+=1
		else:
			if og_user==user_name:
				conversations.append({'Friend (' + friend_name +')': snippet})
			if og_user==bot_name:
				conversations.append({og_user: snippet})
			snippet=''
			fp = sp

	#Append last conversation
	conversations.append({og_user:snippet})
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

	with open(input_folder_path+'/'+friend_name+'Chat.txt', encoding="utf-8") as f:
		lines = f.readlines()

	regex = r"\d{2}/\d{2}/\d{2}, \d{1,2}:\d{2}\s*(am|pm)\s*-\s*" #remove timestamps

	dataset = []

	for line in lines:
		message = re.sub(regex, "", line)
		if remove_placeholders(message):
			continue
		message = remove_links(message)
		message = replace_users(message, contact_name, friend_name, bot_name, your_contact_name)

		dataset.append(message)

	dataset = collate_messages(dataset, friend_name, bot_name, friend_name)
	with open(output_folder_path+'/'+friend_name+'Chat.json', 'w') as file:
		json.dump(dataset, file)
