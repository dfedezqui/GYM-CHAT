import json
import os
import spacy
from spacy.matcher import PhraseMatcher
import unicodedata

# ==========================================
# 1. CONFIGURACIÓN Y CARGA DE DATOS
# ==========================================

# Cargar modelo de Spacy (asegúrate de tenerlo: python -m spacy download es_core_news_sm)
try:
    nlp = spacy.load("es_core_news_sm")
except OSError:
    print("⚠️  AVISO: Modelo de Spacy no encontrado. Ejecuta: python -m spacy download es_core_news_sm")
    nlp = spacy.blank("es")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Usamos el diccionario maestro que creamos antes
DICCIONARIO_PATH = os.path.join(BASE_DIR, "resources", "dictionary.json")

with open(DICCIONARIO_PATH, "r", encoding="utf-8") as f:
    diccionario_data = json.load(f)

# ==========================================
# 2. PREPARACIÓN DE MATCHERS (Cerebro del NLP)
# ==========================================

matcher_entidades = PhraseMatcher(nlp.vocab, attr="LOWER")

# Mapas para traducir de "Texto detectado" -> "Nombre Canónico"
# Ejemplo: "bola" -> "Bíceps"
mapa_canonico = {}
mapa_tipo = {}

def cargar_matcher_desde_json(categoria_json, etiqueta_spacy):
    """
    Lee el JSON, caryga todos los 'inputs' (sinónimos) en el Matcher de Spacy
    y guarda la referencia a su nombre real (canónico).
    """
    lista_items = diccionario_data.get(categoria_json, [])
    
    for item in lista_items:
        nombre_real = item["nombre_canonico"]
        variantes = item["inputs"]
        
        # Guardamos el mapeo inverso para todos los sinónimos
        for v in variantes:
            # Normalizamos un poco al guardar
            mapa_canonico[v.lower()] = nombre_real
            mapa_tipo[nombre_real] = etiqueta_spacy # Sabemos que "Pectoral" es un MUSCULO
            
        # Crear patrones para Spacy
        patterns = [nlp.make_doc(text) for text in variantes]
        matcher_entidades.add(etiqueta_spacy, patterns)

# Cargamos todo dinámicamente desde el JSON
cargar_matcher_desde_json("musculos", "MUSCULO")
cargar_matcher_desde_json("ejercicios", "EJERCICIO")
cargar_matcher_desde_json("equipamiento", "EQUIPO")
cargar_matcher_desde_json("porciones", "PORCION")

# ==========================================
# 3. FUNCIONES DE LIMPIEZA Y EXTRACCIÓN
# ==========================================

def normalizar(texto):
    """Elimina tildes y pone minúsculas para comparaciones básicas de keywords"""
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()

def extraer_entidades(texto):
    """
    Procesa el texto y devuelve listas de entidades CANÓNICAS encontradas.
    Ya no devuelve 'bola', devuelve 'Bíceps'.
    """
    doc = nlp(texto)
    matches = matcher_entidades(doc)
    
    entidades_encontradas = {
        "MUSCULO": [],
        "EJERCICIO": [],
        "EQUIPO": [],
        "PORCION": []
    }

    # Usamos un set para evitar duplicados (ej: si detecta "press" y "press banca")
    # Aquí aplicamos una lógica simple: nos quedamos con todo lo que coincida.
    
    for match_id, start, end in matches:
        etiqueta = nlp.vocab.strings[match_id] # "MUSCULO", "EJERCICIO"...
        span = doc[start:end]
        texto_detectado = span.text.lower()
        
        # Traducir al nombre real usando nuestro mapa
        if texto_detectado in mapa_canonico:
            nombre_real = mapa_canonico[texto_detectado]
            if nombre_real not in entidades_encontradas[etiqueta]:
                entidades_encontradas[etiqueta].append(nombre_real)

    return entidades_encontradas

# ==========================================
# 4. CLASIFICADOR DE INTENCIÓN (Lógica de negocio)
# ==========================================

def clasificar(texto):
    """
    Toma el texto del usuario y devuelve:
    (nombre_funcion, [lista_de_argumentos])
    """
    texto_norm = normalizar(texto)
    ents = extraer_entidades(texto)
    
    musculos = ents["MUSCULO"]
    ejercicios = ents["EJERCICIO"]
    equipos = ents["EQUIPO"]
    porciones = ents["PORCION"]

    # --- PALABRAS CLAVE ---
    saludar_kw = ["hola", "buenos", "buenas", "que tal", "ey"]
    despedir_kw = ["adios", "chao", "hasta luego", "bye"]
    comparar_kw = ["comparar", "diferencia", "distinto", "versus", " vs ", "cual es mejor"]
    explicar_kw = ["explica", "que es", "dime", "hablame", "como", "informacion", "saber"]
    recomendar_kw = ["recomienda", "rutina", "sugiere", "dame", "mejor ejercicio"]

    # 1. SALUDOS / DESPEDIDAS
    if any(k in texto_norm for k in saludar_kw):
        return "saludar", []
    if any(k in texto_norm for k in despedir_kw):
        return "despedir", []

    # 2. LOGICA DE COMPARACIÓN (Requiere 2 entidades)
    if any(k in texto_norm for k in comparar_kw):
        if len(musculos) >= 2:
            return "comparar musculos", [musculos[0], musculos[1]]
        if len(ejercicios) >= 2:
            return "comparar ejercicios", [ejercicios[0], ejercicios[1]]
        # Si compara "pecho" con "sentadilla" (músculo vs ejercicio), es un caso raro,
        # pero podríamos manejarlo o dar error.

    # 3. LOGICA DE EXPLICACIÓN DETALLADA (Variantes y Porciones)
    
    # Caso: Variante ("Como hago press banca con mancuernas")
    if ejercicios and equipos:
        return "explicar variante", [ejercicios[0], equipos[0]]
    
    # Caso: Porción ("Como entreno la parte superior del pecho")
    if musculos and porciones:
        # Mapeamos "Superior" -> "Superior" (ya lo hace el extractor)
        return "explicar porcion", [musculos[0], porciones[0]]
    
    # 4. LOGICA DE RECOMENDACIÓN ("Recomienda ejercicio para pecho")
    if any(k in texto_norm for k in recomendar_kw):
        if musculos:
            tipo = "Compuesto" # Default
            if "aislamiento" in texto_norm or "detalle" in texto_norm:
                tipo = "Aislamiento"
            return "recomendar ejercicio", [musculos[0], tipo]

    # 5. LOGICA SIMPLE (Explicación básica)
    if musculos:
        return "explicar musculo", [musculos[0]]
    
    if ejercicios:
        return "explicar ejercicio", [ejercicios[0]]

    # 6. FALLBACK
    return "no entender", []
