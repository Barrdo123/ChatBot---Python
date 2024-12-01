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
documento_parts = []  # Lista para armazenar as partes do documento

MAX_TOKENS = 6000  # Limite de tokens por requisição
MAX_CHUNK_SIZE = MAX_TOKENS - 1000  # Deixar um buffer de 1000 tokens para a parte da mensagem e o prompt

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
    if opcao == '1':  # Site
        loader = WebBaseLoader(entrada)
    elif opcao == '2':  # PDF
        loader = PyPDFLoader(entrada)
    elif opcao == '3':  # YouTube
        loader = YoutubeLoader.from_youtube_url(entrada, language=['pt'])
    else:
        return "Opção inválida!"

    try:
        lista_documentos = loader.load()
        documento = ''.join(doc.page_content for doc in lista_documentos)
        # Dividir o documento em partes menores, se necessário
        documento_parts = dividir_documento(documento)
        return "Documento carregado com sucesso!"
    except Exception as e:
        return f"Erro ao carregar documento: {e}"

def resposta_bot(mensagem):
    global documento_parts
    respostas = []
    
    # Enviar cada parte do documento separadamente para evitar exceder o limite de tokens
    for i, parte in enumerate(documento_parts):
        mensagens_modelo = [('system', f"Você é amigável e se chama Barrdo, você tem acesso a essa parte dos dados para suas respostas: Parte {i+1}: {parte}")]
        mensagens_modelo.extend(mensagem)
        
        template = ChatPromptTemplate.from_messages(mensagens_modelo)
        chain = template | chat
        resposta = chain.invoke({'documento': parte}).content
        respostas.append(resposta)
    
    return ' '.join(respostas)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send', methods=['POST'])
def send():
    global menssagem
    user_input = request.form['user_input']
    if user_input.lower() == 'x':
        menssagem = []  # Reset the conversation
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
