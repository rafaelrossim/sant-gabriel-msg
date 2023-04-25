# Telegram API
# https://core.telegram.org/bots
# https://api.telegram.org/bot{your_chatid}/getUpdates

# import libs
from flask import jsonify
import requests, os, urllib.request, re, datetime, openai
from app import app
from bs4 import BeautifulSoup

chatid = os.getenv("chatid_group") # chat do grupo
# chatid = os.getenv("chatid_bot") # BOT
apiToken_telegram = os.getenv("token_tlg")
apiToken_openai = os.getenv("token_openai")


def send_telegram(message, chatid):
    """Função que reaiza o envio de mensagem, utilizando a API Telegram

    Args:
        message (str): Mensagem a ser enviada
        chatid (str): ChatID do contato ou grupo desejado a receber a mensagem
    """
    
    apiURL = f'https://api.telegram.org/bot{apiToken_telegram}/sendMessage'

    try:
        requests.post(apiURL, json={'chat_id': chatid, 'text': message})
    except Exception as e:
        print(e)


# def send_telegram_img(ulr_img, chatid):
#     """Função que reaiza o envio de imagens, utilizando a API Telegram
# 
#     Args:
#         ulr_img (str): URL da imagem a ser enviada
#         chatid (str): ChatID do contato ou grupo desejado a receber a mensagem
#     """
# 
#     apiURL = f'https://api.telegram.org/bot{apiToken_telegram}/sendPhoto'
#     
#     with open("santo.jpg", "wb") as f:
#         f.write(ulr_img)
#         
#     try:
#         requests.post(apiURL, files={'photo': open("santo.jpg", 'rb')}, data={'chat_id': chatid})
#     except Exception as e:
#         print(e)


def search_youtube(palavra_chave: str):
    """Função que realiza pesquisa no Youtube

    Args:
        palavra_chave (str): Palavra chave para pesquisa

    Returns:
        url: URL do vídeo encontrado
    """
    
    search_keyword = palavra_chave
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + search_keyword)
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    video_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
    
    return video_url


def req_site(site):
    """Função que realiza o webscrapping da pagina em questão

    Args:
        site(str): Site da empresa

    Returns:
        str: Código de resposta da requisição
    """
    
    headers = {'user-agent': 'Chrome/105.0.0.0'}
    resposta = requests.get(site, headers=headers)    
    resp_code = resposta.status_code
    print("Obtendo dados do site {}, {}\n".format(site, resp_code))
    
    return resposta


def who_was(nome):
    """Função que realiza a busca no OpenAI

    Args:
        nome(str): Nome do santo

    Returns:
        str: Código de resposta da requisição
    """
    
    openai.api_key = apiToken_openai

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="quem foi {}".format(nome),
        temperature=0.1,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    return response["choices"][0]["text"]


@app.route('/liturgia_diaria/', methods=['GET'])
def liturgia_diaria():
    """Função que realiza query na API Liturgia Diária e envia mensagem para o Telegram
    
    Returns:
        json: Toda a liturgia diária
    """
    
    url = 'https://liturgia.up.railway.app/'
    
    r = requests.get(url).json()
    
    # ontendo dados gerais da lirurgia
    json_data  = r['data']
    json_liturgia  = r['liturgia']
    json_cor = r['cor']
    json_prefacio = r['dia']
    
    # enviando dados gerais da liturgia
    send_telegram(f"Liturgia do dia: {json_data} - {json_liturgia}" , chatid)
    send_telegram(f"Cor: {json_cor}", chatid)
    send_telegram(f"Antífona: {json_prefacio}", chatid)
    
    # obtendo primeira leitura
    json_primeiraLeitura_titulo = r['primeiraLeitura']['titulo']
    json_primeiraLeitura_texto = r['primeiraLeitura']['texto']
    json_primeiraLeitura_referencia = r['primeiraLeitura']['referencia']
    
    # enviando dados da primeira leitura
    send_telegram("Primeira leitura:\n\n {} ({})\n\n {}\n\n Palavra do Senhor. Graças a Deus.".format(
        json_primeiraLeitura_titulo, 
        json_primeiraLeitura_referencia, 
        json_primeiraLeitura_texto), 
        chatid
    )    
    
    # obtendo salmo
    json_salmo_refrao = r['salmo']['refrao']
    json_salmo_texto = r['salmo']['texto']
    json_salmo_referencia = r['salmo']['referencia']
    
    # enviando dados de salmo
    send_telegram("Salmo:\n\n {} ({})\n\n {}\n\n".format(
        json_salmo_refrao, 
        json_salmo_referencia, 
        json_salmo_texto), 
        chatid
    )
    
    # verificando se existe segunda leitura
    if r['segundaLeitura'] != "Não há segunda leitura hoje!":
        
        # caso positivo, obtendo dados da segunda leitura
        json_segundaLeitura_titulo = r['segundaLeitura']['titulo']
        json_segundaLeitura_texto = r['segundaLeitura']['texto']
        json_segundaLeitura_referencia = r['segundaLeitura']['referencia']
        
        # enviando dados da segunda leitura
        send_telegram("Segunda leitura:\n\n {} ({})\n\n {}\n\n Palavra do Senhor. Graças a Deus.".format(
            json_segundaLeitura_titulo, 
            json_segundaLeitura_referencia, 
            json_segundaLeitura_texto), 
            chatid
        )
    
    # obtendo evangelho
    json_evangelho_titulo = r['evangelho']['titulo']
    json_evangelho_texto = r['evangelho']['texto']
    json_evangelho_referencia = r['evangelho']['referencia']
    
    # enviando dados do evangelho
    send_telegram("Evangelho:\n\n {} ({})\n\n {}\n\n Palavra da Salvação. Glória a vós, Senhor.".format(
        json_evangelho_titulo, 
        json_evangelho_referencia, 
        json_evangelho_texto), 
        chatid
    )
    
    # obtendo video da homilia diária
    video_yt_homilia = search_youtube("homilia+diaria+padre+paulo+ricardo+hoje")
    send_telegram("Homilia de hoje:\n\n {}".format(video_yt_homilia), chatid)
    
    # obtendo data de hoje e converter a data em formato de dia da semana
    data_hoje = datetime.datetime.now()
    dia_da_semana = data_hoje.strftime("%A")
    
    # criando dict para fazer tradução da semana em português
    dias_da_semana = {
    "Monday": "segundafeira", 
    "Tuesday": "tercafeira",
    "Wednesday": "quartafeira", 
    "Thursday": "quintafeira", 
    "Friday": "sextafeira", 
    "Saturday": "sabado", 
    "Sunday": "domingo"
    }
    
    # obtendo video do terço diário
    video_yt_terco = search_youtube("terco+diario+frei+gilson+"+dias_da_semana[dia_da_semana])
    
    # enviando vídeo do terço diário
    send_telegram("Terço de hoje:\n\n {}".format(video_yt_terco), chatid)
    
    # obtendo dados do santo do dia
    html_req = req_site("https://santo.cancaonova.com/")
    dados_html = BeautifulSoup(html_req.text, 'html.parser')
    
    # obtendo nome do santo do dia
    nome_santo = dados_html.find('h1', class_='entry-title').text
    nome_santo_msg = nome_santo.split(",")[0]
    
    # enviando nome do santo do dia
    send_telegram("Santo(a) do dia: {}".format(nome_santo), chatid)
    
    # obtendo imagem do santo do dia
    # url_img = dados_html.find('img', class_='wp-image-10488 size-full').get('src')
    # url_img_santo = requests.get(url_img).content
    
    # enviando imagem do santo do dia
    # send_telegram_img(url_img_santo, chatid)
    
    # obtendo resumo do santo do dia por chatGPT
    quem_foi = who_was(nome_santo_msg)
    
    # enviando resumo do santo do dia
    send_telegram("{}\n {}, rogai por nós!".format(quem_foi, nome_santo_msg), chatid)
    
    return jsonify(msg = "Liturgia enviada com sucesso!"), 200

# execução de script
if __name__ == "__main__":
    app.run(port=8080)