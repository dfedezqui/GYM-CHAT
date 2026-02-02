import json
import os
import spacy
from spacy.matcher import PhraseMatcher
import unicodedata
from rapidfuzz import process, fuzz
import re

# ==========================================
# 1. CONFIGURACIÓN Y CARGA DE DATOS
# ==========================================
try:
    nlp = spacy.load("es_core_news_sm")
except OSError:
    nlp = spacy.blank("es")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Asegúrate de que la ruta coincida con tu estructura de carpetas
DICCIONARIO_PATH = os.path.join(BASE_DIR,"resources", "dictionary.json") 

with open(DICCIONARIO_PATH, "r", encoding="utf-8") as f:
    diccionario_data = json.load(f)

# ==========================================
# 2. UTILIDADES DE NORMALIZACIÓN
# ==========================================
def normalizar_texto(texto):
    """Elimina acentos, puntuación innecesaria y convierte a minúsculas."""
    texto = texto.lower()
    texto = "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    # Eliminar paréntesis y símbolos para no romper el match
    texto = re.sub(r'[()\[\]/_\-]', ' ', texto)
    return " ".join(texto.split())

# ==========================================
# 3. CONFIGURACIÓN DEL MATCHER
# ==========================================
matcher_entidades = PhraseMatcher(nlp.vocab, attr="LOWER")
mapa_canonico = {}
mapa_tipo = {}
todas_las_variantes = [] # Para el Fuzzy Match global

def cargar_entidades():
    for cat in ["musculos", "ejercicios", "equipamiento", "porciones"]:
        for item in diccionario_data.get(cat, []):
            nombre_real = item["nombre_canonico"]
            inputs = item["inputs"]
            # Guardamos para PhraseMatcher
            patterns = [nlp.make_doc(v.lower()) for v in inputs]
            matcher_entidades.add(nombre_real, patterns)
            # Guardamos para lógica posterior
            for v in inputs:
                v_norm = normalizar_texto(v)
                mapa_canonico[v_norm] = nombre_real
                mapa_tipo[v_norm] = cat
                todas_las_variantes.append(v_norm)

cargar_entidades()

# ==========================================
# 4. LÓGICA DE CLASIFICACIÓN (EL MOTOR)
# ==========================================
def clasificar(texto_original):
    texto = normalizar_texto(texto_original)
    doc = nlp(texto)
    
    # 1. Extraer Entidades detectadas
    matches = matcher_entidades(doc)
    entidades_encontradas = []
    for match_id, start, end in matches:
        span = doc[start:end]
        entidades_encontradas.append({
            "nombre": nlp.vocab.strings[match_id],
            "tipo": "" # Se determina abajo
        })

    # 2. Si no hay matches, intentar Fuzzy Match preventivo por tokens
    if not entidades_encontradas:
        for token in texto.split():
            if len(token) < 4: continue
            # Bajamos a 70 para captar "cuadrisep" o "trizzzeps"
            match_fuzzy = process.extractOne(token, todas_las_variantes, score_cutoff=70)
            if match_fuzzy:
                nombre_c = mapa_canonico[match_fuzzy[0]]
                if not any(e['nombre'] == nombre_c for e in entidades_encontradas):
                    entidades_encontradas.append({"nombre": nombre_c})

    # 3. Organizar entidades por categoría
    res = {"musculos": [], "ejercicios": [], "equipamiento": [], "porciones": []}
    
    # Re-mapear tipos (esto es necesario porque un nombre canónico puede venir de fuzzy)
    for ent in entidades_encontradas:
        nombre = ent["nombre"]
        for cat in diccionario_data:
            for item in diccionario_data[cat]:
                if item["nombre_canonico"] == nombre:
                    if nombre not in res.get(cat, []):
                        res[cat if cat != "porciones" else "porciones"].append(nombre)

    # 4. DETERMINAR FUNCIÓN (Lógica de Intenciones)
    palabras_texto = texto.split()
    
    # Saludos
    if any(p in texto for p in ["hola", "buenos dias", "buenas", "hey", "que tal"]):
        return "saludar", []

    # Despedidas / Agradecimientos
    if any(p in texto for p in ["adios", "chao", "luego", "gracias", "bye", "gracias"]):
        return "despedir", []
    # -------------------------------------------
    # COMPARAR (Reforzado)
    if any(p in texto for p in ["vs", "versus", "comparar", "diferencia", "mejor que", "comparado"]):
        if len(res["ejercicios"]) >= 2:
            return "comparar ejercicios", res["ejercicios"][:2]
        if len(res["musculos"]) >= 2:
            return "comparar musculos", res["musculos"][:2]

    # RECOMENDAR (Reforzado)
    if any(p in texto for p in ["recomienda", "sugiere", "rutina", "entrenar", "hago para", "mejor ejercicio"]):
        tipo_entreno = "Aislamiento" if "aislamiento" in texto else "Compuesto"
        if res["musculos"]:
            return "recomendar ejercicio", [res["musculos"][0], tipo_entreno]

    # EXPLICAR PORCIÓN
    if res["musculos"] and res["porciones"]:
        return "explicar porcion", [res["musculos"][0], res["porciones"][0]]

    # EXPLICAR VARIANTE (Ejercicio + Equipo)
    if res["ejercicios"] and res["equipamiento"]:
        return "explicar variante", [res["ejercicios"][0], res["equipamiento"][0]]

    # EXPLICAR BÁSICO
    if res["ejercicios"]:
        return "explicar ejercicio", [res["ejercicios"][0]]
    if res["musculos"]:
        return "explicar musculo", [res["musculos"][0]]


    return "no entender", []