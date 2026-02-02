import json
import os
import spacy
from spacy.matcher import PhraseMatcher
import unicodedata
from rapidfuzz import process
import re

# ==========================================
# 0. MEMORIA CONVERSACIONAL (estado corto)
# ==========================================
memoria = {
    "ultimo_ejercicio": None,
    "ultimo_musculo": None,
    "ultima_intencion": None
}

# ==========================================
# 1. CONFIGURACIÓN Y CARGA DE DATOS
# ==========================================
try:
    nlp = spacy.load("es_core_news_sm")
except OSError:
    nlp = spacy.blank("es")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DICCIONARIO_PATH = os.path.join(BASE_DIR, "resources", "dictionary.json")

with open(DICCIONARIO_PATH, "r", encoding="utf-8") as f:
    diccionario_data = json.load(f)

# ==========================================
# 2. UTILIDADES DE NORMALIZACIÓN
# ==========================================
def normalizar_texto(texto):
    texto = texto.lower()
    texto = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    texto = re.sub(r"[()\[\]/_\-]", " ", texto)
    return " ".join(texto.split())

# ==========================================
# 3. CONFIGURACIÓN DEL MATCHER
# ==========================================
matcher_entidades = PhraseMatcher(nlp.vocab, attr="LOWER")
mapa_canonico = {}
mapa_tipo = {}
todas_las_variantes = []

def cargar_entidades():
    for cat in ["musculos", "ejercicios", "equipamiento", "porciones"]:
        for item in diccionario_data.get(cat, []):
            nombre_real = item["nombre_canonico"]
            inputs = item["inputs"]

            patterns = [nlp.make_doc(v.lower()) for v in inputs]
            matcher_entidades.add(nombre_real, patterns)

            for v in inputs:
                v_norm = normalizar_texto(v)
                mapa_canonico[v_norm] = nombre_real
                mapa_tipo[v_norm] = cat
                todas_las_variantes.append(v_norm)

cargar_entidades()

# ==========================================
# 4. MOTOR DE CLASIFICACIÓN
# ==========================================
def clasificar(texto_original):
    texto = normalizar_texto(texto_original)
    doc = nlp(texto)

    # --------------------------------------
    # 1. EXTRAER ENTIDADES
    # --------------------------------------
    matches = matcher_entidades(doc)
    entidades_encontradas = []

    for match_id, start, end in matches:
        span = doc[start:end]
        entidades_encontradas.append({
            "nombre": nlp.vocab.strings[match_id]
        })

    # --------------------------------------
    # 2. FUZZY MATCH SI NO HAY MATCHES
    # --------------------------------------
    if not entidades_encontradas:
        for token in texto.split():
            if len(token) < 4:
                continue

            match_fuzzy = process.extractOne(
                token,
                todas_las_variantes,
                score_cutoff=70
            )

            if match_fuzzy:
                nombre_c = mapa_canonico[match_fuzzy[0]]
                if not any(e["nombre"] == nombre_c for e in entidades_encontradas):
                    entidades_encontradas.append({"nombre": nombre_c})

    # --------------------------------------
    # 3. ORGANIZAR POR CATEGORÍAS
    # --------------------------------------
    res = {
        "musculos": [],
        "ejercicios": [],
        "equipamiento": [],
        "porciones": []
    }

    for ent in entidades_encontradas:
        nombre = ent["nombre"]
        for cat in diccionario_data:
            for item in diccionario_data[cat]:
                if item["nombre_canonico"] == nombre:
                    if nombre not in res[cat]:
                        res[cat].append(nombre)

    # --------------------------------------
    # 4. ACTUALIZAR MEMORIA
    # --------------------------------------
    if res["ejercicios"]:
        memoria["ultimo_ejercicio"] = res["ejercicios"][0]

    if res["musculos"]:
        memoria["ultimo_musculo"] = res["musculos"][0]

    palabras = texto.split()

    # --------------------------------------
    # 5. INTENCIONES BÁSICAS
    # --------------------------------------
    if any(p in texto for p in ["hola", "buenos dias", "buenas", "hey", "que tal"]):
        memoria["ultima_intencion"] = "saludar"
        return "saludar", []

    if any(p in texto for p in ["adios", "chao", "luego", "bye", "gracias"]):
        memoria["ultima_intencion"] = "despedir"
        return "despedir", []

    # --------------------------------------
    # 6. COMPARAR
    # --------------------------------------
    if any(p in texto for p in ["vs", "versus", "comparar", "diferencia", "mejor que"]):
        if len(res["ejercicios"]) >= 2:
            memoria["ultima_intencion"] = "comparar ejercicios"
            return "comparar ejercicios", res["ejercicios"][:2]

        if len(res["musculos"]) >= 2:
            memoria["ultima_intencion"] = "comparar musculos"
            return "comparar musculos", res["musculos"][:2]

    # --------------------------------------
    # 7. RECOMENDAR
    # --------------------------------------
    if any(p in texto for p in ["recomienda", "sugiere", "rutina", "entrenar", "mejor ejercicio"]):
        tipo_entreno = "Aislamiento" if "aislamiento" in texto else "Compuesto"
        if res["musculos"]:
            memoria["ultima_intencion"] = "recomendar ejercicio"
            return "recomendar ejercicio", [res["musculos"][0], tipo_entreno]

    # --------------------------------------
    # 8. EXPLICACIONES
    # --------------------------------------
    if res["musculos"] and res["porciones"]:
        memoria["ultima_intencion"] = "explicar porcion"
        return "explicar porcion", [res["musculos"][0], res["porciones"][0]]

    if res["ejercicios"] and res["equipamiento"]:
        memoria["ultima_intencion"] = "explicar variante"
        return "explicar variante", [res["ejercicios"][0], res["equipamiento"][0]]

    if res["ejercicios"]:
        memoria["ultima_intencion"] = "explicar ejercicio"
        return "explicar ejercicio", [res["ejercicios"][0]]

    if res["musculos"]:
        memoria["ultima_intencion"] = "explicar musculo"
        return "explicar musculo", [res["musculos"][0]]

    # --------------------------------------
    # 9. HERENCIA DE CONTEXTO (FOLLOW-UP)
    # --------------------------------------
    if not res["ejercicios"] and res["equipamiento"]:
        if memoria["ultimo_ejercicio"]:
            memoria["ultima_intencion"] = "explicar variante"
            return "explicar variante", [
                memoria["ultimo_ejercicio"],
                res["equipamiento"][0]
            ]

    if texto.startswith("y ") or texto.startswith("¿y"):
        if memoria["ultimo_ejercicio"] and res["equipamiento"]:
            memoria["ultima_intencion"] = "explicar variante"
            return "explicar variante", [
                memoria["ultimo_ejercicio"],
                res["equipamiento"][0]
            ]

    # --------------------------------------
    # 10. FALLBACK
    # --------------------------------------
    memoria["ultima_intencion"] = "no entender"
    return "no entender", []
