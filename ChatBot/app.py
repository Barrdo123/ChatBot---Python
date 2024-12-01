from flask import Flask, request, render_template
import os
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import WebBaseLoader, YoutubeLoader
from langchain.document_loaders import PyPDFLoader

app = Flask(__name__)

api_key = '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'
os.environ['GROQ_API_KEY'] = api_key

chat = ChatGroq(model='llama-3.1-70b-versatile')

menssagem = []
documento = None
documento_parts = []

MAX_TOKENS = 6000  
MAX_CHUNK_SIZE = MAX_TOKENS - 1000 

def dividir_documento(documento):
    """Divide o documento em partes menores com até 6.000 tokens."""
    partes = []
    while len(documento) > MAX_CHUNK_SIZE:
        partes.append(documento[:MAX_CHUNK_SIZE])
        documento = documento[MAX_CHUNK_SIZE:]
    if len(documento) > 0:
        partes.append(documento)
    return partes

def carregar_documento(opcao, entrada):
    global documento, documento_parts
    if opcao == '1': 
        loader = WebBaseLoader(entrada)
    elif opcao == '2':  
        loader = PyPDFLoader(entrada)
    elif opcao == '3':  
        loader = YoutubeLoader.from_youtube_url(entrada, language=['pt'])
    else:
        return "Opção inválida!"

    try:
        lista_documentos = loader.load()
        documento = ''.join(doc.page_content for doc in lista_documentos)

        documento_parts = dividir_documento(documento)
        

        print(f"Documento dividido em {len(documento_parts)} partes.")
        for i, parte in enumerate(documento_parts):
            print(f"Parte {i+1} tem {len(parte)} caracteres.")
        
        return "Documento carregado com sucesso!"
    except Exception as e:
        return f"Erro ao carregar documento: {e}"

def resposta_bot(mensagem):
    global documento_parts
    mensagens_modelo = [('system', 'Você tem acesso às partes do documento carregado.')]
    

    mensagens_modelo.extend(mensagem)


    for i, parte in enumerate(documento_parts):
        print(f"Enviando a Parte {i+1} do documento para o modelo...")
        mensagens_modelo.append(('system', f"Parte {i+1} do documento: {parte}"))

    template = ChatPromptTemplate.from_messages(mensagens_modelo)
    chain = template | chat
    
    try:
        resposta = chain.invoke({'documento': documento_parts}).content
        print(f"Resposta gerada: {resposta}")
        return resposta
    except Exception as e:
        print(f"Erro ao gerar resposta: {e}")
        return f"Erro ao gerar resposta: {e}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send', methods=['POST'])
def send():
    global menssagem
    user_input = request.form['user_input']
    if user_input.lower() == 'x':
        menssagem = [] 
        return {"response": "Foi um prazer, obrigado por usar o BarrdoBot!"}
    
    menssagem.append(('user', user_input))
    bot_response = resposta_bot(menssagem)
    menssagem.append(('assistant', bot_response))
    return {"response": bot_response}

@app.route('/upload', methods=['POST'])
def upload():
    opcao = request.form['option']
    entrada = request.form['input']
    response = carregar_documento(opcao, entrada)
    return {"response": response}

if __name__ == '__main__':
    app.run(debug=True)
