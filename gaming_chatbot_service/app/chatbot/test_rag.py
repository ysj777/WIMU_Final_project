import os
import faiss
import numpy as np
from transformers import BertTokenizer, BertModel
import requests
import google.generativeai as genai
from pathlib import Path
from .search_gamer_1 import search_and_save
import openai
import configparser
from openai import OpenAI
import base64
'''
pip install faiss-gpu
要根據每次query修改 document_path = ""
'''

current_path = os.path.dirname(os.path.abspath(__file__))
config = configparser.ConfigParser()
config.read(os.path.join(current_path, '../config.ini'))

client_openai = OpenAI(
    organization = config['openai']['organization'],
    api_key = config['openai']['api_key']
)

# 設定文件夾路徑
documents_path = Path.joinpath(Path(current_path), f'./result/74934_活動')  # 替換為你的Markdown文件夾路徑

# 假設我們有一個函數可以發送請求到 Gemini Pro API 並獲得生成的回復
def generate_response_with_gemini(query, context):
    api_url = "https://api.geminipro.com/generate"  # 假設這是 Gemini Pro 的 API URL
    payload = {
        "query": query,
        "context": context
    }
    response = requests.post(api_url, json=payload)
    return response.json().get("generated_text", "")

# 生成RAG回覆
def generate_rag_response(query, relevant_documents):
    context = " ".join(relevant_documents)
    response = generate_response_with_gemini(query, context)
    return response

class Chatbot:
    def __init__(self) -> None:
        super().__init__()

        # 加載 BERT 中文模型和 tokenizer
        self.model_name = "bert-base-chinese"
        self.tokenizer = BertTokenizer.from_pretrained(self.model_name)
        self.model = BertModel.from_pretrained(self.model_name)
        self.documents = self.load_markdown_files1(documents_path)
        self.topic_bsn = '74934'
        # 生成文檔嵌入
        self.doc_embeddings = np.array([self.get_embedding(doc) for doc in self.documents]).squeeze()

        # 使用 FAISS 創建索引
        d = self.doc_embeddings.shape[1]  # 嵌入向量的維度
        self.index = faiss.IndexFlatL2(d)  # 使用 L2 距離
        self.index.add(self.doc_embeddings)  # 將文檔嵌入添加到索引中

        self.default_topic = dict()
        self.create_topic()
        self.chat_history = []

    def encode_image(self,image_path):
        with open(Path.joinpath(Path(current_path),image_path), "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
        
    # 加載Markdown文件
    def load_markdown_files(self,path):
        documents = []
        for filename in os.listdir(path):
            if filename.endswith(".md"):
                with open(os.path.join(path, filename), 'r', encoding='utf-8') as file:
                    content = file.read()
                    documents.append(content)
        return documents
    
    def load_markdown_files1(self,path):
        documents = []
        for filename in os.listdir(path):
            for filenames in os.listdir(os.path.join(path, filename)):
                if filenames.endswith(".md"):
                    with open(os.path.join(path, filename, filenames), 'r', encoding='utf-8') as file:
                        content = file.read()
                        print(content)
                        documents.append(content)
        return documents
    
    # 生成嵌入函數
    def get_embedding(self,text):
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True)
        outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).detach().numpy()
    
    # 查詢並檢索相關文檔
    def retrieve_relevant_documents_faiss(self, user_input, index, documents, top_k=5):
        query_embedding = self.get_embedding(user_input).astype('float32')
        distances, indices = index.search(query_embedding, top_k)
        image_list = []
        for i in indices[0]:
                for filenames in os.listdir(f'{documents_path}/{i}'):
                    if len(image_list) < 5:
                        if filenames.endswith(".jpg"):
                            image_list.append(self.encode_image(f'./result/74934_活動/{i}/{filenames}'))

        return [documents[i] for i in indices[0]] , image_list
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
    
    def Greeting(self):
        response = "您好!歡迎來到Strategy Scraper。我可以幫助您了解有關熱門遊戲的最新消息還有相關資訊，請先選擇您想了解的主題。"
        print(response, '\n')
        #processed_response = re.sub(r'\n{2,}', '\n', response.strip())
        return {"role": "assistant","content": response}

    def Chat(self, user_input=None):
        # 主流程
        #query = "鳴潮裡面有什麼角色"
        print(user_input)
        search_and_save(self.topic_bsn, user_input)
        self.documents = self.load_markdown_files1(documents_path)
        self.doc_embeddings = np.array([self.get_embedding(doc) for doc in self.documents]).squeeze()
        # 使用 FAISS 創建索引
        d = self.doc_embeddings.shape[1]  # 嵌入向量的維度
        self.index = faiss.IndexFlatL2(d)  # 使用 L2 距離
        self.index.add(self.doc_embeddings)  # 將文檔嵌入添加到索引中

        relevant_documents , image_list = self.retrieve_relevant_documents_faiss(user_input , self.index, self.documents)
        #print(relevant_documents)
        for i in image_list:
            print(i)
        
        '''
        這邊要改成GPT-4的API、載入retrieved到的documents相關的圖片。
        '''
        content = [
            {
            "type": "text",
            "text": f"你是一個親切的遊戲攻略指引者，你會根據這些文章{relevant_documents}，回答玩家的疑問{user_input}，並給予一段簡單的說明：",
            }
        ]
        for i in image_list:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{i}"
                }
            })
        #print(content)
        response = client_openai.chat.completions.create(
            model="gpt-4o",
            messages = [
                {
                    "role": "user",
                    "content": content
                }
            ],
            max_tokens=300,
        )
        print(response.choices[0].message.content)
        return {"role": "assistant","content": response.choices[0].message.content}
        #print(message)
        response = generate_rag_response(user_input, relevant_documents)
        # Get google API key
        genai.configure(api_key="AIzaSyDqZ2PXZ1NAt3KArw26Ug37_NDojLqp1nk")
        # Define model
        MODEL = "gemini-pro" # "gemini-1.5-flash-latest"
        model = genai.GenerativeModel(MODEL)
        # 構建繁體中文的prompt
        prompt = f"你是一個親切的遊戲攻略指引者，你會根據這些文章{relevant_documents}，回答玩家的疑問{user_input}，並給予一段簡單的說明："
        # 生成內容

        response = model.generate_content(prompt)
        print(response.text)
        return {"role": "assistant","content": response.text}





















