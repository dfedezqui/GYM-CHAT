import json
import os
import spacy
from spacy.matcher import PhraseMatcher
from difflib import get_close_matches
import unicodedata

def normalizar(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, "resources", "entities_spacy.json")

with open(JSON_PATH, "r", encoding="utf-8") as f:
    base_datos = json.load(f)

nlp = spacy.load("es_core_news_sm")

matcher_musculos = PhraseMatcher(nlp.vocab, attr="LOWER")
matcher_segmentos = PhraseMatcher(nlp.vocab, attr="LOWER")
matcher_ejercicios = PhraseMatcher(nlp.vocab, attr="LOWER")
matcher_variantes = PhraseMatcher(nlp.vocab, attr="LOWER")

# Diccionario de sinónimos
SINONIMOS = {
    "deltoides": ["hombro"],
    "pectoral": ["pecho", "tetas"],
    "bíceps": ["bice", "brazo frontal"],
    "tríceps": ["trice", "brazo posterior", "triceps"],
    "cuádriceps": ["cuadriceps", "pierna frontal"],
    "femorales": ["isquios", "pierna trasera"],
    "glúteos": ["gluteo", "trasero", "nalgas"],
    "gemelos": ["pantorrillas"],
    "press banca": ["press plano", "press pecho", "press de banca"],
    "remo con barra": ["remo barra"],
    "peso muerto": ["deadlift"]
}

def expandir_sinonimos(nombre, lista):
    expandidos = [nombre]
    nombre_norm = normalizar(nombre)
    for canonico, aliases in SINONIMOS.items():
        if normalizar(canonico) == nombre_norm or nombre_norm in map(normalizar, aliases):
            expandidos.extend([canonico] + aliases)
            break
    for variante in set(expandidos):
        if variante.lower() not in [x.lower() for x in lista]:
            lista.append(variante)
    return list(set(lista))

musculos_raw, segmentos_raw, ejercicios_raw, variantes_raw = [], [], [], []

for musculo in base_datos.get("musculos", []):
    nombres_musculo = expandir_sinonimos(musculo["nombre"], [])
    musculos_raw.extend(nombres_musculo)
    for nombre in nombres_musculo:
        matcher_musculos.add("MUSCULO", [nlp(nombre)])
    for segmento in musculo["segmentos"]:
        segmentos_raw.append(segmento)
        matcher_segmentos.add("SEGMENTO", [nlp(segmento)])

for ejercicio in base_datos.get("ejercicios", []):
    nombres_ejercicio = expandir_sinonimos(ejercicio["nombre"], [])
    ejercicios_raw.extend(nombres_ejercicio)
    for nombre in nombres_ejercicio:
        matcher_ejercicios.add("EJERCICIO", [nlp(nombre)])
    for variante in ejercicio["variantes"]:
        variantes_raw.append(variante)
        matcher_variantes.add("VARIANTE", [nlp(variante)])

def lematizar(texto):
    return " ".join([token.lemma_ for token in nlp(texto.lower()) if not token.is_stop and token.is_alpha])

def get_matches(text, matcher):
    doc = nlp(text.lower())
    matches = matcher(doc)
    return list(set([doc[start:end].text.lower() for _, start, end in matches]))

def buscar_aproximado(texto, opciones, max_res=1, corte=0.7):
    texto_norm = normalizar(texto)
    opciones_norm = [normalizar(o) for o in opciones]
    candidatos = get_close_matches(texto_norm, opciones_norm, n=max_res, cutoff=corte)
    if candidatos:
        idx = opciones_norm.index(candidatos[0])
        return opciones[idx]
    return None

def extraer_entidades(texto):
    lemmas = lematizar(texto)
    musculos = get_matches(lemmas, matcher_musculos)
    segmentos = get_matches(lemmas, matcher_segmentos)
    ejercicios = get_matches(lemmas, matcher_ejercicios)
    variantes = get_matches(lemmas, matcher_variantes)

    if not musculos:
        for palabra in texto.split():
            m = buscar_aproximado(palabra, musculos_raw)
            if m and m not in musculos: musculos.append(m)
    if not segmentos:
        for palabra in texto.split():
            s = buscar_aproximado(palabra, segmentos_raw)
            if s and s not in segmentos: segmentos.append(s)
    if not ejercicios:
        for palabra in texto.split():
            e = buscar_aproximado(palabra, ejercicios_raw)
            if e and e not in ejercicios: ejercicios.append(e)
    if not variantes:
        for palabra in texto.split():
            v = buscar_aproximado(palabra, variantes_raw)
            if v and v not in variantes: variantes.append(v)

    return musculos, segmentos, ejercicios, variantes

def clasificar(texto):
    texto_lower = texto.lower()
    texto_norm = normalizar(texto_lower)

    musculos, segmentos, ejercicios, variantes = extraer_entidades(texto)

    saludar_kw = ["hola", "buenos dias", "buenas tardes", "saludos", "que tal"]
    despedir_kw = ["adios", "hasta luego", "nos vemos", "chao", "bye"]
    explicar_kw = ["explica", "explicar", "que es", "dime", "hablame", "cuentame", "informacion"]
    comparar_kw = ["comparar", "diferencia", "distinto", "vs", "versus", "entre"]
    recomendar_kw = ["recomienda", "recomiendas", "recomendar", "quiero", "sugerir", "necesito", "mejor", "me gustaria"]

    if any(normalizar(k) in texto_norm for k in saludar_kw):
        return "saludar", []
    if any(normalizar(k) in texto_norm for k in despedir_kw):
        return "despedir", []

    if any(k in texto_norm for k in recomendar_kw) and musculos:
        objetivo = "hipertrofia"
        if "fuerza" in texto_norm:
            objetivo = "fuerza"
        return "recomendar ejercicio", [musculos[0], objetivo]

    if segmentos and musculos:
        return "explicar segmentoMusculo", [musculos[0], segmentos[0]]

    if any(k in texto_norm for k in comparar_kw) and len(musculos) >= 2:
        return "comparar musculos", musculos[:2]

    if any(k in texto_norm for k in explicar_kw) and musculos:
        return "explicar musculo", [musculos[0]]

    if any(k in texto_norm for k in comparar_kw) and len(ejercicios) >= 2:
        return "comparar ejercicios", ejercicios[:2]

    if ejercicios and variantes:
        return "explicar variante", [ejercicios[0], variantes[0]]

    if any(k in texto_norm for k in explicar_kw) and ejercicios:
        return "explicar ejercicio", [ejercicios[0]]

    return "no entender", []
