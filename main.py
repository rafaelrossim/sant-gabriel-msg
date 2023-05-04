# Docs TelegramAPI
# https://core.telegram.org/bots
# https://api.telegram.org/bot{token_telegram}/getUpdates


# importando libs
import requests, os, urllib.request, re, datetime, openai, pytz
from app import app
from bs4 import BeautifulSoup
from flask import jsonify


# declarando variáveis
chatid = os.getenv("chatid_group") # chatid dos grupos
# adcichatid = os.getenv("chatid_bot") # chatid para testes (bot)
chatid_list = list(chatid.split(","))
apiToken_telegram = os.getenv("token_tlg")
apiToken_openai = os.getenv("token_openai")


# declarando funções
def send_telegram(message, chatid, disable_web_page_preview=False):
    """Função que reaiza o envio de mensagem, utilizando a API Telegram

    Args:
        message (str): Mensagem a ser enviada
        chatid (str): ChatID do contato ou grupo desejado a receber a mensagem
    """
    
    apiURL = f'https://api.telegram.org/bot{apiToken_telegram}/sendMessage'
    
    try:
        requests.post(apiURL, json={'chat_id': chatid, 'text': message, 'disable_web_page_preview': disable_web_page_preview})
    except Exception as e:
        print(e)


def send_telegram_img(ulr_img, chatid):
    """Função que realiza o envio de imagens, utilizando a API Telegram

    Args:
        ulr_img (str): URL da imagem a ser enviada
        chatid (str): ChatID do contato ou grupo desejado a receber a mensagem
    """

    apiURL = f'https://api.telegram.org/bot{apiToken_telegram}/sendPhoto'
    
    with open("img.jpg", "wb") as f:
        f.write(ulr_img)
        
    try:
        requests.post(apiURL, files={'photo': open("img.jpg", 'rb')}, data={'chat_id': chatid})
    except Exception as e:
        print(e)


def search_youtube(palavra_chave: str):
    """Função que realiza uma pesquisa no Youtube

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
    """Função que realiza a busca no ChatGPT

    Args:
        nome(str): Nome do Santo(a) de Deus

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
    
    # declarando e solicitnado url da API
    url = 'https://liturgia.up.railway.app/'
    r = requests.get(url).json()
    
    # ontendo dados gerais da lirurgia
    json_data  = r['data']
    json_liturgia  = r['liturgia']
    json_cor = r['cor']
    json_prefacio = r['dia']
    
    # enviando mensagens para uma lista de grupos
    for c in chatid_list:
        print("Enviando mensagem para o chatid {}".format(c))
        
        # enviando dados gerais da liturgia
        send_telegram(f"Liturgia do dia: {json_data} - {json_liturgia}" , c)
        send_telegram(f"Cor: {json_cor}", c)
        send_telegram(f"Antífona: {json_prefacio}", c)
        
        # obtendo primeira leitura
        json_primeiraLeitura_titulo = r['primeiraLeitura']['titulo']
        json_primeiraLeitura_texto = r['primeiraLeitura']['texto']
        json_primeiraLeitura_referencia = r['primeiraLeitura']['referencia']
        
        # enviando dados da primeira leitura
        send_telegram("Primeira leitura:\n\n {} ({})\n\n {}\n\n Palavra do Senhor. Graças a Deus.".format(
            json_primeiraLeitura_titulo, 
            json_primeiraLeitura_referencia, 
            json_primeiraLeitura_texto), 
            c
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
            c
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
                c
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
            c
        )
        
        # obtendo video da homilia diária
        video_yt_homilia = search_youtube("homilia+diaria+padre+paulo+ricardo+hoje")
        send_telegram("Homilia de hoje:\n\n {}".format(video_yt_homilia), c)
        
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
        send_telegram("Terço de hoje:\n\n {}".format(video_yt_terco), c)
        
        # obtendo dados do santo do dia
        html_req = req_site("https://santo.cancaonova.com/")
        dados_html = BeautifulSoup(html_req.text, 'html.parser')

        # obtendo nome do santo do dia
        nome_santo = dados_html.find('h1', class_='entry-title').text
        nome_santo_msg = nome_santo.split(",")[0]
        
        # enviando nome do santo do dia
        send_telegram("""Santo(a) do dia: {}\nSaiba mais: https://santo.cancaonova.com""".format(nome_santo), c, True)
        
        # obtendo imagem do santo do dia
        url_img = dados_html.find_all('img')[1].get('src')
        url_img_santo = requests.get(url_img).content
    
        send_telegram_img(url_img_santo, c)
        send_telegram("""{}, Rogai por nós""".format(nome_santo_msg), chatid)
        
        # obtendo resumo do santo do dia por chatGPT
        # quem_foi = who_was(nome_santo_msg)
        
        # enviando resumo do santo do dia
        # send_telegram("{}\n {}, rogai por nós!".format(quem_foi, nome_santo_msg), c)
    
    return jsonify(msg = "Liturgia enviada com sucesso!"), 200


@app.route('/liturgia_horas/', methods=['GET'])
def liturgia_horas():
    """Função que realiza o envio do liturgia das horas"""
    
    # Obter o timezone do Brasil
    timezone = pytz.timezone('Brazil/East')

    # Obter a hora atual com o timezone do Brasil
    now = datetime.datetime.now(timezone)
    
    # hora atual com timezone
    now_tmz = now.time()
    
    # verificando a hora atual para enviar o ofício das horas
    if now_tmz >= datetime.time(3, 0) and now_tmz < datetime.time(6, 0):
        liturgia_horas = """Liturgia das horas (Matinas) - 03am:\n
        Agora, lábios meus, dizei e anunciai os grandes louvores da Virgem Mãe de Deus. 
         Sede em meu favor, Virgem soberana, livrai-me do inimigo com o Vosso valor.
         Glória seja ao Pai, ao Filho e ao Amor também, que é um só Deus em Pessoas três, 
         agora e sempre, e sem fim. Amém.\n\n
        
        Hino:\n
        Deus Vos salve, Virgem, Senhora do mundo, Rainha dos céus e das virgens, Virgem. 
         Estrela da manhã, Deus Vos salve, cheia de graça divina, formosa e louçã. 
         Daí pressa Senhora, em favor do mundo, pois Vos reconhece como defensora. 
         Deus Vos nomeou desde a eternidade, para a Mãe do Verbo, com o qual criou terra, mar e céus. 
         E Vos escolheu, quando Adão pecou, por esposa de Deus. Deus Vos escolheu, 
         e já muito antes, em Seu tabernáculo morada lhe deu.\n\n
        
        Ouvi, Mãe de Deus, minha oração. Toque em Vosso peito os clamores meus.\n\n
        
        Oração:\n
        Santa Maria, Rainha dos céus, Mãe de Nosso Senhor Jesus Cristo, Senhora do mundo, 
         que a nenhum pecador desamparais e nem desprezais; ponde, Senhora, 
         em mim os olhos de Vossa piedade e alcançai-me de Vosso amado Filho o perdão de todos os meus pecados, 
         para que eu, que agora venero com devoção, Vossa Santa e Imaculada Conceição, 
         mereça na outra vida alcançar o prêmio da bem-aventurança, pelo merecimento do Vosso bendi- to filho, 
         Jesus Cristo, Nosso Senhor, que com o Pai e o Espírito Santo vive e reina para sempre. Amém.\n\n
        """
    
    elif now_tmz >= datetime.time(6, 0) and now_tmz < datetime.time(9, 0):
        
        ofercimento_dia = """Oferecimento do Dia - 06am:\n
        Ofereço-vos, ó meu Deus, em união com o Santíssimo Coração de Jesus e por meio do Imaculado Coração de Maria, 
         as orações, obras, sofrimentos e alegrias deste dia, em reparação de nossas ofensas 
         e por todas as inten- ções pelas quais o Divino Coração está, continuamente, intercedendo em nosso favor.
         Eu Vos ofereço, de modo particular, pelas intenções do nosso Santo Padre, o Papa e por toda a Igreja. Amém.\n\n"""
    
        ofercimento_dia = ofercimento_dia.replace("\n        ", "")
        send_telegram(ofercimento_dia, os.getenv("chatid_bot")) # enviando mensagem para o bot teste
        
        oracao_manha = """Oração da Manhã:\n
        Senhor, meu Deus, no silêncio deste dia que amanhece, venho pedir-Te paz, sabedoria e força. H
         oje quero olhar o mundo com os olhos cheios de amor; ser paciente, compreensivo, humilde, suave e bondoso. 
         Quero ver todos os teus filhos além das aparências, como Tu mesmo os vês, e assim não olhar senão ao bem de cada um.
         Fecha meus ouvidos a toda murmuração; guarda a minha língua de toda maledicência, e que só de amor se encha a minha vida. 
         Quero ser bem-in- tencionado e justo; e que todos aqueles que se aproximarem de mim, sintam a Tua presença. 
         Senhor, reveste-me da tua bondade e que, no decorrer deste dia, eu Te revele a todos. Amém.\n\n"""
         
        oracao_manha = oracao_manha.replace("\n        ", "")
        send_telegram(oracao_manha, os.getenv("chatid_bot")) # enviando mensagem para o bot teste
        
        liturgia_horas = """Liturgia das horas (Prima):\n
        Sede em meu favor, Virgem soberana, livrai-me do inimigo com o Vosso valor. 
         Glória seja ao Pai, ao Filho e ao Amor também, que é um só Deus em Pessoas três, 
         agora e sempre, e sem fim. Amém.\n\n
        
        Hino:\n
        Deus Vos salve, mesa para Deus ornada, coluna sagrada, de grande firme- za; 
         Casa dedicada a Deus sempiterno, sempre preservada Virgem do pecado. Antes que nascida, 
         foste, Virgem Santa, no ventre ditoso de Ana concebida. Sois Mãe criadora dos mortais viventes. 
         Sois dos santos porta dos anjos Senhora. Sois forte esquadrão contra o inimigo, Estrela de Jacó, refúgio do cristão. 
         A Virgem criou Deus no Espírito Santo, e todas as suas obras, com Ela as ornou.\n\n
        
        Ouvi, Mãe de Deus, minha oração. Toque em Vosso peito os clamores meus.\n\n
        
        Oração:\n
        Santa Maria, Rainha dos céus, Mãe de Nosso Senhor Jesus Cristo, Senhora do mundo, 
         que a nenhum pecador desamparais e nem desprezais; ponde, Senhora, 
         em mim os olhos de Vossa piedade e alcançai-me de Vosso amado Filho o perdão de todos os meus pecados, 
         para que eu, que agora venero com devoção, Vossa Santa e Imaculada Conceição, 
         mereça na outra vida alcançar o prêmio da bem-aventurança, pelo merecimento do Vosso bendi- to filho, 
         Jesus Cristo, Nosso Senhor, que com o Pai e o Espírito Santo vive e reina para sempre. Amém.\n\n
        """
        
    elif now_tmz >= datetime.time(9, 0) and now_tmz < datetime.time(12, 0):
        liturgia_horas = """Liturgia das horas (Terça) - 09am:\n
        Sede em meu favor, Virgem soberana, livrai-me do inimigo com o Vosso valor.
         Glória seja ao Pai, ao Filho e ao Amor também, que é um só Deus em Pessoas três, agora e sempre, e sem fim. Amém.\n\n
        
        Hino:\n
        Deus Vos salve trono do grão Salomão, arca do concerto, velo de Gedeão; 
         Íris do céu clara, sarça da visão, favo de Sansão, fluorescente vara; 
         a qual escolheu para ser Mãe sua, e de Vós nasceu o Filho de Deus. 
         Assim Vos livrou da culpa original, de nenhum pecado há em Vós sinal. 
         Vós, que habi- tais lá nas alturas, e tendes Vosso Trono sobre as nuvens puras.\n\n
        
        Ouvi, Mãe de Deus, minha oração. Toque em Vosso peito os clamores meus.\n\n
        
        Oração:\n
        Santa Maria, Rainha dos céus, Mãe de Nosso Senhor Jesus Cristo, Senhora do mundo, 
         que a nenhum pecador desamparais e nem desprezais; ponde, 
         Senhora, em mim os olhos de Vossa piedade e alcançai-me de Vosso amado Filho o perdão de todos os meus pecados, 
         para que eu, que agora venero com devoção, Vossa Santa e Imaculada Conceição, 
         mereça na outra vida alcançar o prêmio da bem-aventurança, pelo merecimento do Vosso bendi- to filho, 
         Jesus Cristo, Nosso Senhor, que com o Pai e o Espírito Santo vive e reina para sempre. Amém.\n\n
        """
        
    elif now_tmz >= datetime.time(12, 0) and now_tmz < datetime.time(15, 0):
        liturgia_horas = """Liturgia das horas (Sexta) - 12pm:\n
        Sede em meu favor, Virgem soberana, livrai-me do inimigo com o Vosso valor. 
         Glória seja ao Pai, ao Filho e ao Amor também, que é um só Deus em Pessoas três, agora e sempre, e sem fim. Amém.\n\n
        
        Hino:\n
        Deus Vos salve Virgem da Trindade templo, alegria dos anjos, da pureza exemplo; 
         que alegrais os tristes, com vossa clemência, horto de deleite, palma de paciência. Sois terra
         bendita e sacerdotal, sois da castidade símbolo real. Cidade do Altíssimo, porta oriental; 
         sois a mesma graça, Virgem singular. Qual lírio cheiroso, entre espinhas duras, tal sois Vós, Senhora, entre as criaturas.\n\n
        
        Ouvi, Mãe de Deus, minha oração. Toque em Vosso peito os clamores meus.\n\n
        
        Oração:\n
        Santa Maria, Rainha dos céus, Mãe de Nosso Senhor Jesus Cristo, Senhora do mundo, 
         que a nenhum pecador desamparais e nem desprezais; ponde, Senhora, 
         em mim os olhos de Vossa piedade e alcançai-me de Vosso amado Filho o perdão de todos os meus pecados, 
         para que eu, que agora venero com devoção, Vossa Santa e Imaculada Conceição, 
         mereça na outra vida alcançar o prêmio da bem-aventurança, pelo merecimento do Vosso bendi- to filho, 
         Jesus Cristo, Nosso Senhor, que com o Pai e o Espírito Santo vive e reina para sempre. Amém.\n\n
        """
        
        # obtendo video da homilia diária
        video_yt_homilia = search_youtube("homilia+diaria+padre+paulo+ricardo+hoje")
        send_telegram("Homilia de hoje:\n\n {}".format(video_yt_homilia), os.getenv("chatid_bot"))
        
    elif now_tmz >= datetime.time(15, 0) and now_tmz < datetime.time(18, 0):
        liturgia_horas = """Liturgia das horas (Noa) - 03pm:\n
        Sede em meu favor, Virgem soberana, livrai-me do inimigo com o Vosso valor. 
         Glória seja ao Pai, ao Filho e ao Amor também, que é um só Deus em Pessoas três, agora e sempre, e sem fim. Amém.\n\n
        
        Hino:\n
        Deus Vos salve cidade de torres guarnecida, de Davi com armas bem forta- lecidas. 
         De suma caridade sempre abrasada, do dragão à força foi por Vós prostrada. 
         Ó mulher tão forte! Ó invicta Judite! Vós acalentastes o sumo Davi! Do Egito o curador, 
         de Raquel nasce, do mundo o Salvador Maria no-lo deu. Toda é formosa minha companheira, 
         n'Ela não há mácula da culpa primeira.\n\n
        
        Ouvi, Mãe de Deus, minha oração. Toque em Vosso peito os clamores meus.\n\n
        
        Oração:\n
        Santa Maria, Rainha dos céus, Mãe de Nosso Senhor Jesus Cristo, Senhora do mundo, 
         que a nenhum pecador desamparais e nem desprezais; ponde, Senhora, em mim os olhos de Vossa piedade 
         e alcançai-me de Vosso amado Filho o perdão de todos os meus pecados, 
         para que eu, que agora venero com devoção, Vossa Santa e Imaculada Conceição, 
         mereça na outra vida alcançar o prêmio da bem-aventurança, pelo merecimento do Vosso bendi- to filho, 
         Jesus Cristo, Nosso Senhor, que com o Pai e o Espírito Santo vive e reina para sempre. Amém.\n\n 
        """
        
    elif now_tmz >= datetime.time(18, 0) and now_tmz < datetime.time(21, 0):
        liturgia_horas = """Liturgia das horas (Vesperas) - 06pm:\n
        Sede em meu favor. Virgem soberana, livrai-me do inimigo com o Vosso valor.
         Glória seja ao Pai, ao Filho e ao Amor também, que é um só Deus em Pessoas três,
         agora e sempre, e sem fim. Amém.\n\n
        
        Hino:\n
        Deus Vos salve, relógio, que, andando atrasado, serviu de sinal ao Verbo
         Encarnado. Para que o homem suba às sumas alturas, desce Deus dos céus para as criaturas.
         Com os raios claros do Sol da Justiça, Resplandece a Virgem, dando ao sol cobiça.
         Sois lírio formoso, que cheiro respira, entre os espinhos da serpente a ira.
         Vós aquebrantais com Vosso poder os cegos errados Vós aluminais.
         Fizestes nascer Sol tão fecundo, e como com nuvens cobristes o mundo.\n\n

        Ouvi, Mãe de Deus, minha oração. Toque em Vosso peito os clamores meus.\n\n

        Oração:\n
        Santa Maria, Rainha dos Céus, Mãe de Nosso Senhor Jesus Cristo, Senhora do mundo,
         que a nenhum pecador desamparais e nem deseprezais; ponde, Senhora,
         em mim os olhos de Vossa piedade e alcançai-me de Vosso amado Filho o perdão de todos os meus pecados,
         para que agora venero com devoção, Vossa Santa e imaculada Conceição,
         mereça na outra vida alcançar o prêmio da bem-aventurança,
         pelo merececimento do Vosso bendito filho, Jesus Cristo, Nosso Senhor,
         que com Pai e o Espirito Santo vive e reina para sempre. Amém.\n\n
        """
        
    elif now_tmz >= datetime.time(21, 0) and now_tmz < datetime.time(0, 0):
        
        oracao_noite = """Oração da Noite - 09pm:\n
        Meu Deus e meu Senhor, obrigado por mais um dia de vida! Eu vos agrade- ço todo bem que me concedestes praticar, 
         e vos suplico perdão e miseri- córdia pelo mal que cometi, em pensamentos, palavras, obras e omissões. 
         Em vossas mãos eu entrego a minha vida e meus trabalhos, ó meu bom Pai! E enquanto eu estiver dormindo, 
         guardai-me na vossa paz e no vosso amor! Abençoai, ó bom Jesus, esta casa, este lar, 
         e que todos estejamos sempre de coração aberto para receber a vossa divina graça. Amém.\n\n"""
        
        oracao_noite = oracao_noite.replace("\n        ", "")
        send_telegram(oracao_noite, os.getenv("chatid_bot")) # enviando mensagem para o bot teste
        
        liturgia_horas = """Liturgia das horas (Completas):\n
        Rogai a Deus, Vós, Virgem, nos converta, que a Sua ira se aparte de nós. Sede em meu favor, Virgem soberana, 
         livrai-me do inimigo com o Vosso valor. Glória seja ao Pai, ao Filho e ao Amor também, 
         que é um só Deus em Pessoas três, agora e sempre, e sem fim. Amém.\n\n
        
        Hino:\n
        Deus Vos salve, Virgem, Mãe Imaculada, rainha de clemência, de estrelas coroadas. Vós
         acima os anjos sois purificada; de Deus a mão direita estás de ouro ornada. Por Vós, Mãe da graça, 
         mereçamos ver, a Deus nas alturas, com todo o prazer. Pois sois a esperança dos pobres errantes, 
         e seguro porto para os nave- gantes. Estrela do mar e saúde certa, e porta que estás para o céu aberta. 
         É óleo derramado, Virgem, Vosso nome, e os Vossos servos vos hão sempre amados.\n

        Ouvi, Mãe de Deus, minha oração. Toque em Vosso peito os clamores meus.\n

        Oração:\n
        Santa Maria, Rainha dos céus, Mãe de Nosso Senhor Jesus Cristo, Senhora do mundo, 
         que a nenhum pecador desamparais e nem desprezais; ponde, Senhora, 
         em mim os olhos de Vossa piedade e alcançai-me de Vosso amado Filho o perdão de todos os meus pecados, 
         para que eu, que agora venero com devoção, Vossa Santa e Imaculada Conceição, 
         mereça na outra vida alcançar o prêmio da bem-aventurança, pelo merecimento do Vosso bendi- to filho, 
         Jesus Cristo, Nosso Senhor, que com o Pai e o Espírito Santo vive e reina para sempre. Amém.\n\n
        
        Oferecimento:\n
        Humildes oferecemos a Vós, Virgem Pia, estas orações, porque, em nossa guia, 
         vades Vós adiante e na agonia, Vós nos animeis, ó doce Virgem Maria. Amém.   
        """
    
    # tratando string para remover espaços em branco
    liturgia_horas = liturgia_horas.replace("\n        ", "")
    
    # send_telegram(liturgia_horas, c)
    send_telegram(liturgia_horas, os.getenv("chatid_bot")) # enviando mensagem para o bot teste
    
    # retornando a liturgia das horas
    return jsonify(msg = "Liturgia das horas enviada com sucesso!"), 200

# execução de script
if __name__ == "__main__":
    app.run(port=8080)