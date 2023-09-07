import urllib.parse
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
# imports chatbot
import nltk
nltk.download('punkt')
nltk.download('rslp')
from nltk.corpus import stopwords
nltk.download('stopwords')
import string
import bs4 as bs
import urllib.request
import re
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


driver = webdriver.Chrome(ChromeDriverManager().install())
print("Acessando WhatsappWeb...")
driver.get('https://web.whatsapp.com/')
driver.maximize_window()
print('Escaneie o QRCode e aperte Enter')
input()

def saudacao():
    return 'Olá, bem vindo ao seu assistente pessoal, estou programado para responder perguntas sobre assuntos gerais, sobre o que você deseja saber? "por favor, seja muito especifico, se possível, utilize apenas uma palavra"'


def abreConversaContato(contato):
    contato.click()

    

def lerUltimaMensagem():
    try:
        mensagens = driver.find_elements_by_css_selector('span.copyable-text')
        ultimo_elemento = mensagens[-1]
        ultima_mensagem = ultimo_elemento.text
        return ultima_mensagem
    except:
        print('Nenhuma mensagem encontrada')
        return ''


def achaContatosComMensagensNovas():
    contatos = driver.find_elements_by_css_selector('span[aria-label="Não lidas"]')
    if(len(contatos) > 0):
        print(f"existem {len(contatos)} mensagens não lidas")
        return contatos

def mandarMensagem(mensagem):
    campo_mensagem = driver.find_elements_by_css_selector("div[contenteditable='true'")[1]
    campo_mensagem.click()
    campo_mensagem.send_keys(mensagem)
    campo_mensagem.send_keys(Keys.ENTER)
    
def identificaPalavraParaDefinirAssunto():
    continua_procurando_assunto = True
    while continua_procurando_assunto:
        assunto = lerUltimaMensagem()
        if assunto != saudacao():
            continua_procurando_assunto = False
            return assunto
        else:
            continue
        

        
    
def stemming(tokens):
  stemmer = nltk.stem.RSLPStemmer()
  novotexto = []
  for token in tokens:
    novotexto.append(stemmer.stem(token.lower()))
  return novotexto

removePontuacao = dict((ord(punctuation), None) for punctuation in string.punctuation)

def preprocessa(documento):
  return stemming(nltk.word_tokenize(documento.lower().translate(removePontuacao), language='portuguese'))

def geradorrespostas(pergunta, sentencas):
      resposta = ''
      sentencas.append(pergunta)
    
      word_vectorizer = TfidfVectorizer(tokenizer=preprocessa, stop_words=stopwords.words('portuguese'))
      all_word_vectors = word_vectorizer.fit_transform(sentencas)
      similar_vector_values = cosine_similarity(all_word_vectors[-1], all_word_vectors)
      similar_sentence_number = similar_vector_values.argsort()[0][-2]
    
      matched_vector = similar_vector_values.flatten()
      matched_vector.sort()
      vector_matched = matched_vector[-2]
    
      if vector_matched == 0:
          resposta = resposta + "Me desculpe, não entendi o que você pediu."
      else:
          resposta = resposta + sentencas[similar_sentence_number]
      return resposta


def respondePergunta(pergunta, sentencas):
    resposta = geradorrespostas(pergunta, sentencas)
    return resposta
    

def perguntaParaUsuario(assunto, sentencas):
    mensagem_pedir_pergunta = f"Faça uma pergunta sobre {assunto.capitalize()}, ou então diga 'sair'"
    mensagem_outra_pergunta = f"Faça outra pergunta sobre {assunto.capitalize()}, ou diga 'sair'"
    mandarMensagem(mensagem_pedir_pergunta)
    continue_dialog = True
    
    while continue_dialog:
        human_text = lerUltimaMensagem()
        resposta = respondePergunta(human_text, sentencas)
        if human_text.lower() == 'sair':
            continue_dialog = False
            mandarMensagem("Até a próxima.")
            break
        elif human_text == mensagem_pedir_pergunta or resposta == human_text or human_text == mensagem_outra_pergunta:
            continue
        else:
            mandarMensagem(resposta)
            mandarMensagem(mensagem_outra_pergunta)
        sentencas.remove(human_text)
             
    
  
        
def iniciaBot(assunto):
    
    try:
        # Aqui buscamos a página sobre o BRASIL. Caso queira mudar o tema basta colocar o link para outra página.
        # Você pode também optar por obter dados de várias páginas diferentes, basta definir uma lista de links e iterar sobre elas.
        parametro_url = urllib.parse.quote(assunto)
        codigo_html = urllib.request.urlopen(f'https://pt.wikipedia.org/wiki/{parametro_url}')
        codigo_html = codigo_html.read()
        
        # Processa o código HTML lido
        html_processado = bs.BeautifulSoup(codigo_html, 'lxml')
        
        # Busca todos parágrafos do texto
        paragrafos = html_processado.find_all('p')
        
        texto = ''
        
        # Percorre parágrafos e concatena textos
        for p in paragrafos:
          texto += p.text
        
        # Normaliza para minúsculas
        texto = texto.lower()
        texto = re.sub(r'\[[0-9]*\]', ' ', texto)
        texto = re.sub(r'\s+', ' ', texto)
        sentencas = nltk.sent_tokenize(texto, language='portuguese')
        sentencas[10:15]
        
        perguntaParaUsuario(assunto, sentencas)
    except:
        mandarMensagem('Desculpe, não consegui achar nada relacionada a esse assunto na minha base de dados!')


def iniciarConversa():
    ultima_mensagem = lerUltimaMensagem().lower()
    saudacoes_entrada = ("olá", "bom dia", "boa tarde", "boa noite", "oi", "como vai", "e aí")
    
    if ultima_mensagem in saudacoes_entrada:
        saudacao_texto = saudacao()
        mandarMensagem(saudacao_texto)
        assunto = identificaPalavraParaDefinirAssunto()
        iniciaBot(assunto)
        
    
        
def fecharConversaAtual():
        mais_opcoes = driver.find_elements_by_css_selector('div[aria-label="Mais opções"]')[1]
        mais_opcoes.click()
        fechar_conversa = driver.find_element_by_css_selector('div[aria-label="Fechar conversa"]')
        fechar_conversa.click()
    

while True:
    try:
        contatos = achaContatosComMensagensNovas()
        for contato in contatos:
            abreConversaContato(contato)
            iniciarConversa()
            fecharConversaAtual()

    except Exception as e:
        continue
