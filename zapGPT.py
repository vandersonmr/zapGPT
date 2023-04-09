import os
import sys
import openai
import chromadb
import OAIWrapper
import random

openai.api_key = os.getenv("OPENAI_API_KEY")
oai = OAIWrapper.OAIWrapper()

def load_zap_chat_log(filename):
    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()

    filtered_lines = []
    for line in lines:
        if "<Media omitted>" not in line:
            try:
                timestamp, content = line.strip().split(" - ", 1)
                user_id, message = content.split(": ", 1)
                filtered_lines.append((user_id, message))
            finally:
                continue

    return filtered_lines

def gen_proompt_to_imitate(user_conversation, max_size):
    proompt = """Describe in details the away that a user chatts based on the examples I will give.
                 You should focus on the language used, and the write style, not the content.
                 You anwser should include examples of the user chatting patterns and the language that the user uses.
                 Pick some of the parts of the message to give as example. Follows messages from this user: """
    examples = [user_id+': '+msg for user_id, msg in user_conversation[-max_size:]]
    proompt = proompt + '\n'.join(examples)
    proompt_to_imitate = oai.chat_completion(proompt)
    return proompt_to_imitate

def gen_next_msgs(user_id, user_description, context):
    proompt_name = "You are going to imitate an user named: " + user_id
    proompt_description = "This user texts looks like as follow: " + user_description
    proompt_context = "These were the last messsages on the conversation: "+ "\n".join([user+': '+msg for user, msg in context])
    proompt_question = """Give me five possible messages, the messages should be independents from each other, and should be folow ups to the last messages on the conversation.
                          Your anwser should only include the messages.
                          It is really important that each message have some relation with the last messages in the conversation.
                          Each message should have just one line and it should just contains messages from the user you are imitating."""
    proompt = proompt_name + '\n' + proompt_description + '\n' + proompt_question + '\n' + proompt_context
    msgs = oai.chat_completion(proompt)
    return msgs.strip(user_id+':').split('\n')

conversation = load_zap_chat_log(sys.argv[1])
user_to_imitate = sys.argv[2]
user_to_talk_to = sys.argv[3]
user_conversation = [(user_id, message) for user_id, message in conversation if  user_to_imitate in user_id]

user_description = gen_proompt_to_imitate(user_conversation, 31)
print("\nUser description: {}\n\n".format(user_description))

while(True):
    context = conversation[-5:]
    possible_msgs = gen_next_msgs(user_to_imitate, user_description, context)
    for i, msg in enumerate(possible_msgs):
        print("({}) {}".format(i, msg))

    print("Which msg (msg id) do you choose: ")
    msg_id = int(input())
    next_msg = possible_msgs[msg_id]
    conversation.append((user_to_imitate, next_msg))

    print(user_to_imitate + ': ' + next_msg)
    print("Input the next message in the conversation:")
    awnser_msg = input()
    conversation.append((user_to_talk_to, awnser_msg))



