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

idioma = "pt-BR"
r = sr.Recognizer()
API_KEY = "suakey"

# === Falar com voz ===
def falar(texto):
    tts = gTTS(text=texto, lang=idioma)
    tts.save("resposta.mp3")
    playsound("resposta.mp3")
    os.remove("resposta.mp3")

# === Verificador de cor (olhos) ===
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
    falar(f"{resultado}")

# === Busca DuckDuckGo ===
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
        return f"Agora são {datetime.now().strftime('%H:%M')}."
    elif "data" in pergunta or "dia" in pergunta:
        return f"Hoje é {datetime.now().strftime('%d/%m/%Y')}."
    elif pergunta in ("oi", "olá", "ola", "capina","lote", "tudo bem"):
        return "Olá, meu nome é Capina Lote."

    try:
        resultado = eval(pergunta)
        return f"Resposta matemática: {resultado}"
    except:
        pass

    try:
        traducao = GoogleTranslator(source='auto', target='pt').translate(pergunta)
        if traducao != pergunta:
            return f"Tradução: {traducao}"
    except:
        pass

    try:
        wikipedia.set_lang("pt")
        return wikipedia.summary(pergunta, sentences=2)
    except:
        try:
            return buscar_wikipedia_detalhes(pergunta)
        except:
            return buscar_duckduckgo(pergunta)

    return "Não entendi o comando."

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

    # Olhos: verificar cor
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
            falar(resposta)
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

# === Entrada principal ===
def ouvir_ou_digitar():
    escolha = input("Digite 'voz' para falar ou 'texto' para digitar: ")
    if escolha == "voz":
        with sr.Microphone(device_index=1) as source:
            print("Fale algo...")
            audio = r.listen(source)
        try:
            return r.recognize_google(audio, language="pt-BR")
        except:
            return "Não entendi o áudio"
    else:
        return input("Digite sua pergunta: ")

while True:
 
    comando = ouvir_ou_digitar()
    if any(p in comando.lower() for p in ("imagem", "print", "foto", "capturar", "tela")):
        selecionar_tela()
    else:
        resposta = responder(comando)
        print("Capina Lote disse:", resposta)
        falar(resposta)
