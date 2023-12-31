import os
import sys

import openai
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma
# import constants
from flask import Flask, request, jsonify

app = Flask(__name__)

os.environ["OPENAI_API_KEY"] = "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"

PERSIST = False

query = None

if PERSIST and os.path.exists("persist"):
    print("Reusing index...\n")
    vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
    index = VectorStoreIndexWrapper(vectorstore=vectorstore)
else:
    loader = TextLoader("data/data.txt")  # Use this line if you only need data.txt
    if PERSIST:
        index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory": "persist"}).from_loaders([loader])
    else:
        index = VectorstoreIndexCreator().from_loaders([loader])

chain = ConversationalRetrievalChain.from_llm(
    llm=ChatOpenAI(model="gpt-3.5-turbo"),
    retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
)

chat_history = []

@app.route('/')
def home():
    return "Welcome to the home page!", 200

@app.route('/ask', methods=['POST'])
def ask_question():
    global chat_history
    data = request.get_json()
    question = data.get('question')

    if question:
        result = chain({"question": question, "chat_history": chat_history})
        response = result['answer']
        chat_history.append((question, response))
        print(chat_history)
        return jsonify({'answer': response}), 200
    else:
        return jsonify({'message': 'Bad request'}), 400

if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)
