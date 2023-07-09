# Docs TelegramAPI
# https://core.telegram.org/bots
# https://api.telegram.org/bot{token_telegram}/getUpdates


# importando libs
import requests, os, urllib.request, re, datetime, pytz
from app import app
from bs4 import BeautifulSoup
from flask import jsonify, request
from extractor.ExtractorService import ExtractorService


# declarando variáveis
chatid = os.getenv("chatid_group_liturgia") # chatid dos grupos
# chatid = os.getenv("chatid_bot_liturgia") # chatid para testes (bot)
chatid_list = list(chatid.split(","))
apiToken_telegram = os.getenv("token_tlg_liturgia")
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


@app.route('/liturgia_diaria/', methods=['GET'])
def liturgia_diaria():
    """Função que realiza o envio da liturgia diária para os grupos do Telegram

    Returns:
        JSON: Mensagem de sucesso ou erro
    """
    
    # Inicializando classe
    liturgy = ExtractorService.getScrapy()
    
    # Obtendo dados da liturgia
    data = str(liturgy['date'])
    titulo_liturgia = str(liturgy['entry_title'])
    cor = str(liturgy['color'])
    
    # Obtendo dados da primeira leitura
    titulo_primeira_leitura = str(liturgy['readings']['first_reading']['head']).replace(".", "")
    passagem_primeira_leitura = str(liturgy['readings']['first_reading']['title']).split("Primeira Leitura ")[1]
    primeira_leitura = str(liturgy['readings']['first_reading']['text']).replace(".", ". ")
    resposta_primeira_leitura = str(liturgy['readings']['first_reading']['footer']+" "+str(liturgy['readings']['first_reading']['footer_response']))
    
    # Obtendo dados do salmo
    try:
        passagem_salmo = str(liturgy['readings']['psalm']['title']).split("Responsório ")[1]
    except IndexError:
        passagem_salmo = str(liturgy['readings']['psalm']['title']).split("Responsório ")[0]
    salmo = str(liturgy['readings']['psalm']['content_psalm']).replace("', '", "\n\n").replace("[", "").replace("]", "")
    reposta_salmo = str(liturgy['readings']['psalm']['response']).replace(".", "")
    
    # Obtendo dados da segunda leitura caso exista
    try:
        titulo_segunda_leitura = str(liturgy['readings']['second_reading']['head']).replace(".", "")
        passagem_segunda_leitura = str(liturgy['readings']['second_reading']['title']).split("Segunda Leitura ")[1]
        segunda_leitura = str(liturgy['readings']['second_reading']['text']).replace(".", ". ")
        resposta_segunda_leitura = str(liturgy['readings']['second_reading']['footer']+" "+str(liturgy['readings']['second_reading']['footer_response']))
    # Caso não haja segunda leitura, define como None
    except KeyError:
        segunda_leitura = None
        print(f"{str(liturgy['date'])}: Não há segunda leitura hoje!")
    
    # Obtendo dados do evangelho
    titulo_evangelho = str(liturgy['readings']['gospel']['head_response'])
    passagem_evangelho = str(liturgy['readings']['gospel']['title']).split("Evangelho ")[1]
    evangelho = str(liturgy['readings']['gospel']['text']).replace(".", ". ")
    resposta_evangelho = str(liturgy['readings']['gospel']['footer']+" "+str(liturgy['readings']['gospel']['footer_response']))
    
    # Obtendo dados da proclamação do evangelho
    all_html = str(liturgy['readings']['gospel']['all_html'])
    soup = BeautifulSoup(all_html, 'html.parser')
    proclamacao_html = soup.find_all('p', align="justify")
    
    # Tratando dados da proclamação do evangelho
    list_proclamacao = []
    for p in proclamacao_html[:2]:
        p = str(p.text).replace("\n", "").replace(" — ", "").replace("   +  ", " ✠ ").replace(".", "").lstrip().rstrip()
        list_proclamacao.append(p)
    
    proclamacao = list_proclamacao[0]
    
    # enviando liturgia para os grupos do Telegram
    for c in chatid_list:
        send_telegram(f"Liturgia do dia: {data} - {titulo_liturgia}", c)
        send_telegram(f"Cor: {cor}", c)
        send_telegram(f"Primeira leitura:\n\n{titulo_primeira_leitura} {passagem_primeira_leitura}\n\n{primeira_leitura}\n\n{resposta_primeira_leitura}", c)
        send_telegram(f"Salmo:\n\n{reposta_salmo} ({passagem_salmo})\n\n{salmo}", c)
        
        # enviando segunda leitura caso exista
        if segunda_leitura != None:
            send_telegram(f"Segunda leitura:\n\n{titulo_segunda_leitura} {passagem_segunda_leitura}\n\n{segunda_leitura}\n\n{resposta_segunda_leitura}", c)
        
        send_telegram(f"Evangelho:\n\n{proclamacao}\n{passagem_evangelho}\n\n{titulo_evangelho}\n\n{evangelho}\n\n{resposta_evangelho}", c)
        
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
        
        # enviado imagem do santo do dia
        send_telegram_img(url_img_santo, c)
        send_telegram("""{}, Rogai por nós""".format(nome_santo_msg), c)
     
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
    
    # enviando mensagens para uma lista de grupos
    for c in chatid_list:
    
        # verificando a hora atual para enviar o ofício das horas
        if now_tmz >= datetime.time(3, 0) and now_tmz < datetime.time(6, 0):
            oracao_inicial = """Ofício da Imaculada Conceição:\n
            Deus vos salve Virgem, Filha de Deus Pai!\n
            Deus vos salve Virgem, Mãe de Deus Filho!\n
            Deus vos salve Virgem, Esposa do Dívino Espírito Santo\n
            Deus vos salve Virgem, Templo e Sacrário da Santíssima Trindade!\n\n
            """
            
            # tratando strings para envio
            oracao_inicial = oracao_inicial.replace("\n         ", "")
            oracao_inicial = oracao_inicial.replace("      ", "")
            oracao_inicial = oracao_inicial.replace("   ", "")
            send_telegram(oracao_inicial, c)
            
            liturgia_horas = """Ofício da Imaculada Conceição (Matinas):\n
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
            mereça na outra vida alcançar o prêmio da bem-aventurança, pelo merecimento do Vosso bendito filho, 
            Jesus Cristo, Nosso Senhor, que com o Pai e o Espírito Santo vive e reina para sempre. Amém.\n\n
            """
            send_telegram("Assista o Ofício da Imaculada Conceição (Matinas) 👇\n\nhttps://www.youtube.com/watch?v=zhAYIkD5xhI", c)
        
        elif now_tmz >= datetime.time(6, 0) and now_tmz < datetime.time(9, 0):
            ofercimento_dia = """Oferecimento do Dia:\n
            Ofereço-vos, ó meu Deus, em união com o Santíssimo Coração de Jesus e por meio do Imaculado Coração de Maria, 
            as orações, obras, sofrimentos e alegrias deste dia, em reparação de nossas ofensas 
            e por todas as intenções pelas quais o Divino Coração está, continuamente, intercedendo em nosso favor. 
            Eu Vos ofereço, de modo particular, pelas intenções do nosso Santo Padre, o Papa e por toda a Igreja. Amém.\n\n"""
            
            # tratando strings para envio
            ofercimento_dia = ofercimento_dia.replace("\n         ", "")
            ofercimento_dia = ofercimento_dia.replace("      ", "")
            ofercimento_dia = ofercimento_dia.replace("   ", "")
            send_telegram(ofercimento_dia, c)
            
            oracao_manha = """Oração da Manhã:\n
            Senhor, meu Deus, no silêncio deste dia que amanhece, venho pedir-Te paz, sabedoria e força.
            Hoje quero olhar o mundo com os olhos cheios de amor; ser paciente, compreensivo, humilde, suave e bondoso. 
            Quero ver todos os teus filhos além das aparências, como Tu mesmo os vês, e assim não olhar senão ao bem de cada um.
            Fecha meus ouvidos a toda murmuração; guarda a minha língua de toda maledicência, e que só de amor se encha a minha vida. 
            Quero ser bem-intencionado e justo; e que todos aqueles que se aproximarem de mim, sintam a Tua presença. 
            Senhor, reveste-me da tua bondade e que, no decorrer deste dia, eu Te revele a todos. Amém.\n\n"""
            
            # tratando strings para envio
            oracao_manha = oracao_manha.replace("\n         ", "")
            oracao_manha = oracao_manha.replace("      ", "")
            oracao_manha = oracao_manha.replace("   ", "")
            send_telegram(oracao_manha, c)
            
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
                
            liturgia_horas = """Ofício da Imaculada Conceição (Prima):\n
            Sede em meu favor, Virgem soberana, livrai-me do inimigo com o Vosso valor. 
            Glória seja ao Pai, ao Filho e ao Amor também, que é um só Deus em Pessoas três, 
            agora e sempre, e sem fim. Amém.\n\n
            
            Hino:\n
            Deus Vos salve, mesa para Deus ornada, coluna sagrada, de grande firmeza; 
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
            mereça na outra vida alcançar o prêmio da bem-aventurança, pelo merecimento do Vosso bendito filho, 
            Jesus Cristo, Nosso Senhor, que com o Pai e o Espírito Santo vive e reina para sempre. Amém.\n\n
            """
            
            send_telegram("Assista o Ofício da Imaculada Conceição (Prima) 👇\n\nhttps://www.youtube.com/watch?v=_t_1MA693WE", c)
            
        elif now_tmz >= datetime.time(9, 0) and now_tmz < datetime.time(12, 0):
            liturgia_horas = """Ofício da Imaculada Conceição (Terça):\n
            Sede em meu favor, Virgem soberana, livrai-me do inimigo com o Vosso valor.
            Glória seja ao Pai, ao Filho e ao Amor também, que é um só Deus em Pessoas três,
            agora e sempre, e sem fim. Amém.\n\n
            
            Hino:\n
            Deus Vos salve trono do grão Salomão, arca do concerto, velo de Gedeão; 
            Íris do céu clara, sarça da visão, favo de Sansão, fluorescente vara; 
            a qual escolheu para ser Mãe sua, e de Vós nasceu o Filho de Deus. 
            Assim Vos livrou da culpa original, de nenhum pecado há em Vós sinal. 
            Vós, que habitais lá nas alturas, e tendes Vosso Trono sobre as nuvens puras.\n\n
            
            Ouvi, Mãe de Deus, minha oração. Toque em Vosso peito os clamores meus.\n\n
            
            Oração:\n
            Santa Maria, Rainha dos céus, Mãe de Nosso Senhor Jesus Cristo, Senhora do mundo, 
            que a nenhum pecador desamparais e nem desprezais; ponde, 
            Senhora, em mim os olhos de Vossa piedade e alcançai-me de Vosso amado Filho o perdão de todos os meus pecados, 
            para que eu, que agora venero com devoção, Vossa Santa e Imaculada Conceição, 
            mereça na outra vida alcançar o prêmio da bem-aventurança, pelo merecimento do Vosso bendito filho, 
            Jesus Cristo, Nosso Senhor, que com o Pai e o Espírito Santo vive e reina para sempre. Amém.\n\n
            """
            
            send_telegram("Assista o Ofício da Imaculada Conceição (Terça) 👇\n\nhttps://www.youtube.com/watch?v=EAcVI43BKvo", c)
            
        elif now_tmz >= datetime.time(12, 0) and now_tmz < datetime.time(15, 0):
            oracao_antes_refeicoes = """Oração antes das refeições:\n
            Em nome do Pai +, do Filho e do Espírito Santo. Amém.\n\n
            Este pão e esta união, abençoai, Senhor!
            Abençoai, Senhor, a mesa deste lar, e na mesa do Céu guardai-nos um lugar!
            Abençoai, Senhor, a nós e a esta comida, providenciai a quem não tem.
            E fazei-nos servir-Vos fielmente, toda a vida. Amém.
            Pai-Nosso, Ave-Maria, Glória ao Pai.\n\n
            """
            
            # tratando strings para envio
            oracao_antes_refeicoes = oracao_antes_refeicoes.replace("\n         ", "")
            oracao_antes_refeicoes = oracao_antes_refeicoes.replace("      ", "")
            oracao_antes_refeicoes = oracao_antes_refeicoes.replace("   ", "")
            send_telegram(oracao_antes_refeicoes, c)
            
            oracao_depois_refeicoes = """Oração depois das refeições:\n
            Em nome do Pai +, do Filho e do Espírito Santo. Amém.\n\n
            Por este pão, por esta união, obrigado, Senhor!
            Somos vossa Igreja doméstica! Senhor, conservai-a unida e feliz!!
            Somos vossa família reunida, como sinal do vosso amor! Guardai-nos felizes e unidos!
            Obrigado, Senhor, por esta refeição!
            Ensinai-nos a repartir o pão com os mais pobres! Amém.
            Pai-Nosso, Ave-Maria, Glória ao Pai.\n\n    
            """
            
            # tratando strings para envio
            oracao_depois_refeicoes = oracao_depois_refeicoes.replace("\n         ", "")
            oracao_depois_refeicoes = oracao_depois_refeicoes.replace("      ", "")
            oracao_depois_refeicoes = oracao_depois_refeicoes.replace("   ", "")
            send_telegram(oracao_depois_refeicoes, c)
            
            liturgia_horas = """Ofício da Imaculada Conceição (Sexta):\n
            Sede em meu favor, Virgem soberana, livrai-me do inimigo com o Vosso valor. 
            Glória seja ao Pai, ao Filho e ao Amor também, que é um só Deus em Pessoas três,
            agora e sempre, e sem fim. Amém.\n\n
            
            Hino:\n
            Deus Vos salve Virgem da Trindade templo, alegria dos anjos, da pureza exemplo; 
            que alegrais os tristes, com vossa clemência, horto de deleite, palma de paciência. Sois terra
            bendita e sacerdotal, sois da castidade símbolo real. Cidade do Altíssimo, porta oriental; 
            sois a mesma graça, Virgem singular. Qual lírio cheiroso, entre espinhas duras, 
            tal sois Vós, Senhora, entre as criaturas.\n\n
            
            Ouvi, Mãe de Deus, minha oração. Toque em Vosso peito os clamores meus.\n\n
            
            Oração:\n
            Santa Maria, Rainha dos céus, Mãe de Nosso Senhor Jesus Cristo, Senhora do mundo, 
            que a nenhum pecador desamparais e nem desprezais; ponde, Senhora, 
            em mim os olhos de Vossa piedade e alcançai-me de Vosso amado Filho o perdão de todos os meus pecados, 
            para que eu, que agora venero com devoção, Vossa Santa e Imaculada Conceição, 
            mereça na outra vida alcançar o prêmio da bem-aventurança, pelo merecimento do Vosso bendito filho, 
            Jesus Cristo, Nosso Senhor, que com o Pai e o Espírito Santo vive e reina para sempre. Amém.\n\n
            """
            
            send_telegram("Assista o Ofício da Imaculada Conceição (Sexta) 👇\n\nhttps://www.youtube.com/watch?v=YV1H_cwOJj4", c)
            
            # obtendo video da homilia diária
            video_yt_homilia = search_youtube("homilia+diaria+padre+paulo+ricardo+hoje")
            send_telegram("Homilia de hoje:\n\n {}".format(video_yt_homilia), c)
            
        elif now_tmz >= datetime.time(15, 0) and now_tmz < datetime.time(18, 0):
            # obtendo video do terço da misericordia
            video_yt_terco_misericordia = search_youtube("terco+da+misericordia+Instituto+Hesed")
            
            # enviando vídeo do terço da misericordia
            send_telegram("Terço da misericórdia:\n\n {}".format(video_yt_terco_misericordia), c)
            
            liturgia_horas = """Ofício da Imaculada Conceição (Nona):\n
            Sede em meu favor, Virgem soberana, livrai-me do inimigo com o Vosso valor. 
            Glória seja ao Pai, ao Filho e ao Amor também, que é um só Deus em Pessoas três, 
            agora e sempre, e sem fim. Amém.\n\n
            
            Hino:\n
            Deus Vos salve cidade de torres guarnecida, de Davi com armas bem fortalecidas. 
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
            mereça na outra vida alcançar o prêmio da bem-aventurança, pelo merecimento do Vosso bendito filho, 
            Jesus Cristo, Nosso Senhor, que com o Pai e o Espírito Santo vive e reina para sempre. Amém.\n\n 
            """
            
            send_telegram("Assista o Ofício da Imaculada Conceição (Nona) 👇\n\nhttps://www.youtube.com/watch?v=Fcd87wtc8LE", c)
            
        elif now_tmz >= datetime.time(18, 0) and now_tmz < datetime.time(21, 0):
            liturgia_horas = """Ofício da Imaculada Conceição (Vesperas):\n
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
            
            send_telegram("Assista o Ofício da Imaculada Conceição (Vesperas) 👇\n\nhttps://www.youtube.com/watch?v=a0hdBl_oKuE", c)
            
        elif now_tmz >= datetime.time(21, 0) and now_tmz < datetime.time(23, 0):
            oracao_noite = """Oração da Noite:\n
            Meu Deus e meu Senhor, obrigado por mais um dia de vida! Eu vos agradeço todo bem que me concedestes praticar, 
            e vos suplico perdão e misericórdia pelo mal que cometi, em pensamentos, palavras, obras e omissões. 
            Em vossas mãos eu entrego a minha vida e meus trabalhos, ó meu bom Pai! E enquanto eu estiver dormindo, 
            guardai-me na vossa paz e no vosso amor! Abençoai, ó bom Jesus, esta casa, este lar, 
            e que todos estejamos sempre de coração aberto para receber a vossa divina graça. Amém.\n\n"""
            
            # tratando strings para envio
            oracao_noite = oracao_noite.replace("\n         ", "")
            oracao_noite = oracao_noite.replace("      ", "")
            oracao_noite = oracao_noite.replace("   ", "")
            send_telegram(oracao_noite, c)
            
            liturgia_horas = """Ofício da Imaculada Conceição (Completas):\n
            Rogai a Deus, Vós, Virgem, nos converta, que a Sua ira se aparte de nós. Sede em meu favor, Virgem soberana, 
            livrai-me do inimigo com o Vosso valor. Glória seja ao Pai, ao Filho e ao Amor também, 
            que é um só Deus em Pessoas três, agora e sempre, e sem fim. Amém.\n\n
            
            Hino:\n
            Deus Vos salve, Virgem, Mãe Imaculada, rainha de clemência, de estrelas coroadas. Vós
            acima os anjos sois purificada; de Deus a mão direita estás de ouro ornada. Por Vós, Mãe da graça, 
            mereçamos ver, a Deus nas alturas, com todo o prazer. Pois sois a esperança dos pobres errantes, 
            e seguro porto para os navegantes. Estrela do mar e saúde certa, e porta que estás para o céu aberta. 
            É óleo derramado, Virgem, Vosso nome, e os Vossos servos vos hão sempre amados.\n

            Ouvi, Mãe de Deus, minha oração. Toque em Vosso peito os clamores meus.\n

            Oração:\n
            Santa Maria, Rainha dos céus, Mãe de Nosso Senhor Jesus Cristo, Senhora do mundo, 
            que a nenhum pecador desamparais e nem desprezais; ponde, Senhora, 
            em mim os olhos de Vossa piedade e alcançai-me de Vosso amado Filho o perdão de todos os meus pecados, 
            para que eu, que agora venero com devoção, Vossa Santa e Imaculada Conceição, 
            mereça na outra vida alcançar o prêmio da bem-aventurança, pelo merecimento do Vosso bendito filho, 
            Jesus Cristo, Nosso Senhor, que com o Pai e o Espírito Santo vive e reina para sempre. Amém.\n\n
            
            Oferecimento:\n
            Humildes oferecemos a Vós, Virgem Pia, estas orações, porque, em nossa guia, 
            vades Vós adiante e na agonia, Vós nos animeis, ó doce Virgem Maria. Amém.   
            """
            
            send_telegram("Assista o Ofício da Imaculada Conceição (Completas) 👇\n\nhttps://www.youtube.com/watch?v=JTOm6WU3Fbo", c)
            send_telegram("Assista o Oferecimento do Ofício da Imaculada Conceição 👇\n\nhttps://www.youtube.com/watch?v=DgzV3caL-3o", c)
    
        # tratando strings para envio
        liturgia_horas = liturgia_horas.replace("\n         ", "")
        liturgia_horas = liturgia_horas.replace("      ", "")
        liturgia_horas = liturgia_horas.replace("   ", "")
        send_telegram(liturgia_horas, c)
    
    # retornando a liturgia das horas
    return jsonify(msg = "Liturgia das horas enviada com sucesso!"), 200


@app.route('/recados/', methods=['POST'])
def recados():
    """Função que realiza o envio de recados para os grupos do telegram"""
    
    # obtendo dados de texto
    data = request.get_data(as_text=True)
    
    data = data.lower()
    
    # enviando mensagem para uma lista de grupos
    for c in chatid_list:
        send_telegram(f"Recados da paróquia:\n{data}", c)
    
    # retornando mensagem de envio
    return jsonify(msg = "Recados enviados com sucesso!"), 200


# execução de script
if __name__ == "__main__":
    app.run(port=8080)