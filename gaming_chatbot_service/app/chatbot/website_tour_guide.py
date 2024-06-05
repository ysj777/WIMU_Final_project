from collections import Counter
from .rag import create_pinecone, enconder, search_query, retrival, google_api
import google.generativeai as genai
import re
import markdown
import os
from pathlib import Path

current_path = os.path.dirname(os.path.abspath(__file__))

def genapi(content):
    GOOGLE_API_KEY = 'AIzaSyB1XplucLezXPIXy99_vUAYWpb5gxa7WXM'
    genai.configure(api_key=GOOGLE_API_KEY)

    safetySettings =  [
                {
                    "category": "HARM_CATEGORY_DANGEROUS",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
            ]
    model = genai.GenerativeModel('gemini-pro', safety_settings = safetySettings)
    response = model.generate_content(content)
    return response.text

class Chatbot:
    def __init__(self) -> None:
        super().__init__()

        self.index = create_pinecone()
        print("Pinecone index created successfully.")
        self.default_topic = dict()
        self.create_topic()
        self.chat_history = []

    def RAG(self, query):
        """
        Your Assignment 2
        """
        index = create_pinecone()
        embed_query = enconder(query)
        matches = search_query(index, embed_query)
        top3_hit_result = retrival(matches, index)
        answer = google_api(query, top3_hit_result)
        return answer

    def create_topic(self):
        """
        Input : None 
        Output : default topic

        Default topic options are provided to LLM as reference topics when users have no other ideas.
        You can set how to provide default topics to the large language model yourself, such as manually setting topics or using other methods.
        """
        with open(Path.joinpath(Path(current_path), f'./defaul_topics/test.md'), 'r', encoding='utf-8') as f:
            content = f.read()
            self.default_topic = content

    def decide_action(self, response):
        """
        Input : response 
        Output : LLM choose action to do

        You can modify the behavior detection here, 
        adding tasks or storing information for the large language model to act upon as needed.
        """
        
        task = {
            'Introduce website information' : "Introducing the website based on predefined topics when the user wishes to get a general understanding of the website structure.", 
            'Answer Question' : 'If the user is asking about some information that you think a Space Science and Engineering department website may have, then answer the questions about the website based on the user response.',
            'Exception': 'If the user asks about some question that you think the website does not have the answer, you can answer the question with your common sense. And redirect the user to ask about the information about the website.',
            'End Chat' : 'When the user want to end this chat, say goodbye to him/her.'
        }

        task_module = ""
        for idx, (title, task_describe) in enumerate(task.items()):
            task_module += f"{idx+1} {title} : {task_describe}, "

        text = genapi(f"You are an action-selection bot. Based on the current user's response and the task modules, \
                      please decide what action to take and output one of the numbers from the task module. \
                      The task modules are as follows {task_module} {response}。")

        if '1' in text:
            action = 'Introduce website information'
        elif '2' in text:
            action = 'Answer Question'
        elif '3' in text:
            action = 'Exception'
        else:
            action = 'End Chat'
        return action
    
    def Greeting(self):
        response = "您好!歡迎來到Strategy Scraper。我可以幫助您了解有關熱門遊戲的最新消息還有相關資訊，請先選擇您想了解的主題。"
        print(response, '\n')
        #processed_response = re.sub(r'\n{2,}', '\n', response.strip())
        return {"role": "assistant","content": response}

    def Chat(self, user_input=None):
        """
        Input : None 
        Output : None

        You can modify the chat flow of your chatbot according to your own settings.
        
        text = genapi(f"You are a website navigation staff member and give a brief introduction \
                      Just a short greeting and a couple of sentences will do; no additional information is needed.")"""    
        print(self.default_topic)
        response  = genapi(f'這裡有使用者提出的遊戲類別{user_input}，請依照以下內容:{self.default_topic}，提供該遊戲的相關標題和連結。其中Post Subject代表文章標題，Post URL代表文章連結。')
        
        print(response, '\n')
        return {"role": "assistant","content": response}
        
        
if __name__ == '__main__':
    website_tour_guid = Chatbot()
    website_tour_guid.Chat()