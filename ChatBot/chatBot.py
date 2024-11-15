import os
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.document_loaders import PyPDFLoader

api_key = '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'
os.environ['GROQ_API_KEY'] = api_key

chat = ChatGroq(model = 'llama-3.1-70b-versatile')

def carrega_site():
  url_site = input('Digite a url do site: ')
  loader = WebBaseLoader(url_site)
  lista_documentos = loader.load()
  documento = ''
  for doc in lista_documentos:
    documento += doc.page_content
  return documento

def carrega_pdf():
  caminho_pdf = 'pdf do colab.pdf'
  loader = PyPDFLoader(caminho_pdf)
  lista_documentos = loader = loader.load()
  documento = ''
  for doc in lista_documentos:
    documento += doc.page_content
  return documento

def carrega_youtube():
  url_video = input('Digite a url do video: ')
  loader = YoutubeLoader.from_youtube_url(
      url_video,
      language = ['pt'])
  lista_documentos = loader.load()
  documento = ''
  for doc in lista_documentos:
    documento += doc.page_content
  return documento

def resposta_bot(menssagem, documento):
  menssagens_modelo = [('system', 'Você é amigavel e se chama Barrdo, você tem acesso a esses dados para suas respostas: {documento}')]
  menssagens_modelo += menssagem
  template = ChatPromptTemplate.from_messages(menssagens_modelo)
  chain = template | chat
  return chain.invoke({'documento': documento}).content


print('Olá seja bem vindo!')

texto_selecão = '''Digite 1 se quiser conversar de acordo com algum site
digite 2 se quiser conversar de acordo com algum pdf
digite 3 se quiser conversar de acordo com algum video do youtube
Digite 4 se quiser conversar com o bot padrão
'''

selecao = input(texto_selecão)

while True:
  if selecao == '1':
    documento = carrega_site()
    break
  if selecao == '2':
    documento = carrega_pdf()
    break
  if selecao == '3':
    documento = carrega_youtube()
    break
  if selecao == '4':
    print('Olá! eu sou o Barrdo, como posso te ajudar?')
    break
  else:
    print('Digite uma opção válida')
    selecao = input(texto_selecão)


menssagem = []

while True:
  pergunta = input('usuario: ')
  if pergunta.lower() == 'x':
    break
  menssagem.append(('user', pergunta))
  resposta = resposta_bot(menssagem, documento)
  menssagem.append(('assistant', resposta))
  print(f"Barrdo: {resposta}")

print("Foi um prazer, obrigado por usar o BarrdoBot!")

