import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import wikipedia
import wikitextparser as wtp
from deep_translator import GoogleTranslator
import mss, mss.tools
import tkinter as tk
import keyboard
import turtle
import time
idioma = "pt-BR"
r = sr.Recognizer()
API_KEY = "key"
#janela
wn=turtle.Screen()
wn.title("ambiente grafico")
wn.setup(width=500,height=500)
wn.tracer(1)

# Registra as formas
wn.register_shape("mic.gif")
wn.register_shape("t.gif")
wn.register_shape("b.gif")
wn.register_shape("f.gif")

# Cria uma tartaruga para cada imagem e posiciona manualmente
t1 = turtle.Turtle()
t1.penup()
t1.shape("mic.gif")

t2 = turtle.Turtle()
t2.penup()
t2.shape("f.gif")



t4 = turtle.Turtle()
t4.penup()
t4.shape("t.gif")

t1.goto(-200, -180)
t2.goto(10, -180)
t4.goto(190, -180)

def clique(x,y):
    if t1.distance(x, y) < 50:
        mic()
    if t2.distance(x, y) < 50:
        ler()

    if t4.distance(x, y) < 50:
        selecionar_tela()

def mic():
    with sr.Microphone() as source:
        print("Fale algo...")
        audio = r.listen(source)
    try:
        texto = r.recognize_google(audio, language="pt-BR")
        if any(p in texto.lower() for p in ("imagem", "print", "foto", "capturar", "tela")):
            selecionar_tela()
        print("Você disse:", texto)
        resposta = responder(texto)
        print("Capina Lote disse:", resposta)
        falar(resposta)
        return texto
    except sr.UnknownValueError:
        print("Não entendi o áudio.")
        return "Não entendi o áudio"
    except sr.RequestError as e:
        print(f"Erro ao solicitar resultados; {e}")
        return "Erro no reconhecimento de fala"

def buscar_duckduckgo(pergunta):
    url = f"https://duckduckgo.com/html/?q={pergunta}"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    resultados = soup.find_all("a", class_="result__a")
    if resultados:
        return resultados[0].text
    return "Nada encontrado no DuckDuckGo e na Wikipedia."


# === Busca Wikipedia ===
def buscar_wikipedia_detalhes(titulo):
    url = "https://pt.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "format": "json",
        "titles": titulo
    }
    resp = requests.get(url, params=params)
    if resp.status_code == 200:
        pages = resp.json()["query"]["pages"]
        page = next(iter(pages.values()))
        if "revisions" in page:
            texto = page["revisions"][0]["*"]
            parsed = wtp.parse(texto)
            if parsed.sections:
                return parsed.sections[0].string.strip()
    return buscar_duckduckgo(titulo)


# === Responder ===
def responder(pergunta):
    pergunta = pergunta.lower()
    pergunta = pergunta.replace("x", "*").replace("vezes","*").replace("mais","+").replace("menos","-").replace("dividido","/")

    if "hora" in pergunta:
        resposta = f"Agora são {datetime.now().strftime('%H:%M')}."
        mostrar_texto(resposta)
        falar(resposta)
        return resposta
    elif "data" in pergunta or "dia" in pergunta:
        resposta = f"Hoje é {datetime.now().strftime('%d/%m/%Y')}."
        mostrar_texto(resposta)
        falar(resposta)
        return resposta
    elif pergunta in ("oi", "olá", "ola", "capina","lote", "tudo bem"):
        resposta = "Olá, meu nome é Indianos Atentos."
        mostrar_texto(resposta)
        falar(resposta)
        return resposta

    try:
        resultado = eval(pergunta)
        resposta = f"Resposta matemática: {resultado}"
        mostrar_texto(resposta)
        falar(resposta)
        return resposta
    except:
        pass

    try:
        traducao = GoogleTranslator(source='auto', target='pt').translate(pergunta)
        if traducao != pergunta:
            resposta = f"Tradução: {traducao}"
            mostrar_texto(resposta)
            falar(resposta)
            return resposta
    except:
        pass

    try:
        wikipedia.set_lang("pt")
        resposta = wikipedia.summary(pergunta, sentences=2)
        mostrar_texto(resposta)
        falar(resposta)
        return resposta
    except:
        try:
            resposta = buscar_wikipedia_detalhes(pergunta)
            mostrar_texto(resposta)
            falar(resposta)
            return resposta
        except:
            resposta = buscar_duckduckgo(pergunta)
            mostrar_texto(resposta)
            falar(resposta)
            return resposta

    resposta = "Não entendi o comando."
    mostrar_texto(resposta)
    falar(resposta)
    return resposta


t = turtle.Turtle()
t.clear()
def mostrar_texto(texto):
    global t
    wn.bgcolor("white")  # Opcional: definir cor de fundo

    t.hideturtle()
    t.penup()
    t.goto(0, 0)
    t.write(texto, align="center", font=("Arial", 16, "normal"))
def ler():
    pergunta = input("Digite sua pergunta: ")
    print(responder(pergunta))

def verificar_cor(imagem):
    root = tk.Tk()
    img = tk.PhotoImage(file=imagem)

    w, h = img.width(), img.height()
    total_r, total_g, total_b = 0, 0, 0
    total_pixels = w * h

    for y in range(h):
        for x in range(w):
            pixel = img.get(x, y)
            if isinstance(pixel, str):
                r = int(pixel[1:3], 16)
                g = int(pixel[3:5], 16)
                b = int(pixel[5:7], 16)
            else:
                r, g, b = pixel
            total_r += r
            total_g += g
            total_b += b

    root.destroy()

    avg_r = total_r // total_pixels
    avg_g = total_g // total_pixels
    avg_b = total_b // total_pixels

    # === Classificação ===
    if avg_r > 140 and avg_g > 120 and avg_b > 110:
        resultado = "Branco detectado"
    elif avg_r < 120 and avg_g < 110 and avg_b < 100:
        resultado = "Negro detectado"

    else:
        resultado = "Tonalidade indefinida"

    print(f"Capina Lote disse (olhos): {resultado}")
    print(f"(Valores médios: R={avg_r}, G={avg_g}, B={avg_b})")


# === Captura de tela ===
def capturar_area(x1, y1, x2, y2):
    left = min(x1, x2)
    top = min(y1, y2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)

    with mss.mss() as sct:
        monitor = {"top": top, "left": left, "width": width, "height": height}
        img = sct.grab(monitor)
        mss.tools.to_png(img.rgb, img.size, output="tela_selecionada.png")

    # Verificar cor dos olhos
    verificar_cor("tela_selecionada.png")

    # OCR
    with open("tela_selecionada.png", "rb") as f:
        response = requests.post(
            "https://api.ocr.space/parse/image",
            files={"file": f},
            data={"apikey": API_KEY, "language": "eng"}
        )

    if response.status_code == 200 and "ParsedResults" in response.json():
        result = response.json()
        texto_extraido = result["ParsedResults"][0]["ParsedText"].strip()
        if texto_extraido:
            print("Texto OCR:", texto_extraido)
            resposta = responder(texto_extraido)
            print("Capina Lote disse:", resposta)
        else:
            print("Nenhum texto foi extraído da imagem.")
    else:
        print("Erro na requisição OCR:", response.text)


# === Seleção com mouse ===
def selecionar_tela():
    coords = {}
    rect_id = None

    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.attributes("-alpha", 0.3)

    canvas = tk.Canvas(root, cursor="cross")
    canvas.pack(fill="both", expand=True)

    def iniciar(event):
        nonlocal rect_id
        coords["x1"], coords["y1"] = event.x, event.y
        rect_id = canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="red", width=2)

    def arrastar(event):
        if rect_id:
            canvas.coords(rect_id, coords["x1"], coords["y1"], event.x, event.y)

    def finalizar(event):
        coords["x2"], coords["y2"] = event.x, event.y
        root.destroy()
        capturar_area(coords["x1"], coords["y1"], coords["x2"], coords["y2"])

    canvas.bind("<ButtonPress-1>", iniciar)
    canvas.bind("<B1-Motion>", arrastar)
    canvas.bind("<ButtonRelease-1>", finalizar)

    root.mainloop()


def falar(texto):
    global t
    """
    Fluxo Seguro de Fala para a IA (indianos atentos)
    Evita travamentos de permissão criando nomes únicos sequenciais.
    """
    try:
        # 1. CAPTURA DO TEMPO: O relógio gera um número único para ESTA execução
        timestamp_atual = int(time.time())
        nome_arquivo = f"audio_{timestamp_atual}.mp3"
        print(f"[Voz] Gerando arquivo exclusivo: {nome_arquivo}")

        # 2. CRIAÇÃO: A biblioteca gTTS escreve o arquivo usando a variável fixa
        tts = gTTS(text=texto, lang=idioma)
        tts.save(nome_arquivo)

        # 3. REPRODUÇÃO: O playsound segura o script aqui até o áudio terminar
        print(f"[Voz] Reproduzindo áudio de {len(texto)} caracteres...")
        playsound(nome_arquivo)
        
        # 4. LIBERAÇÃO E LIMPEZA: O áudio terminou de tocar! 
        # A variável 'nome_arquivo' ainda guarda o mesmo nome do início do fluxo.
        print(f"[Voz] Tentando apagar {nome_arquivo}...")
        try:
            os.remove(nome_arquivo)
            print("[Voz] Arquivo limpo com sucesso!")
            t.clear()
        except Exception as erro_permissao:
            # Se o Windows travar, o except captura e não deixa o robô morrer
            print(f"[Voz] O Windows reteve o arquivo temporariamente, mas o fluxo continua seguro. Erro: {erro_permissao}")

    except Exception as e:
        print(f"[Voz] Erro geral no fluxo de áudio: {e}")




wn.onscreenclick(clique)
wn.update()
