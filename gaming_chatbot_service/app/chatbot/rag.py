import google.generativeai as genai
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
import textwrap

def create_pinecone():
    pc = Pinecone(
        api_key='86960e02-0d81-402c-88a3-bd146bafcb84',
        environment="gcp-starter"
    )
    index_name = 'retrieval-augmentation-generation'
    index = pc.Index(index_name)
    return index

def enconder(query):
    model = SentenceTransformer('thenlper/gte-large-zh')
    embed_query = model.encode(query)
    return embed_query

def search_query(index, embed_query):
    matches = index.query(
        vector=embed_query.tolist(),
        top_k=5,
        include_values=False
    )
    return matches

def retrival(matches, index):
    retrival_data = []
    for item in matches.matches:
        result = index.fetch([item.id])
        retrival_data.append(result['vectors'][item.id].metadata)

    top3_hit_result = ""
    for i, data in enumerate(retrival_data):
        top3_hit_result += f"No.{i+1} data: {data['text']}\n"
        top3_hit_result += f"No.{i+1} url source: {data['source']}\n"
    return top3_hit_result

def google_api(query, top3_hit_result):
    genai.configure(api_key='AIzaSyB1XplucLezXPIXy99_vUAYWpb5gxa7WXM')

    model = genai.GenerativeModel("gemini-pro")

    prompt = textwrap.dedent("""QUESTION: '{query}'
        PASSAGE: '{relevant_passage}'
        You are a great assistant. There are a total of 5 pieces of searched information here. \
        Please extract the relevant parts of each piece of information based on the user's question \
        and organize it into complete and understandable content and reply to the user. Make sure there \
        are no omission, and provide the source URL of the information:
        """).format(query=query, relevant_passage=top3_hit_result)

    answer = model.generate_content(prompt)
    return answer

if __name__ == '__main__':
    query = '系上有哪些獎學金?'

    index = create_pinecone()
    embed_query = enconder(query)
    matches = search_query(index, embed_query)
    top3_hit_result = retrival(matches, index)
    answer = google_api(query, top3_hit_result)

    print("------------------------------------------------------------")
    print(answer.text)
    print("------------------------------------------------------------")