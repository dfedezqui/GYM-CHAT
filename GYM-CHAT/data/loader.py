import json
import os
import random

# ==========================================
# CARGA DE DATOS (Igual que antes)
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "resources")

with open(os.path.join(JSON_PATH, "exercises.json"), "r", encoding="utf-8") as f:
    ejercicios_data = json.load(f)
with open(os.path.join(JSON_PATH, "muscles.json"), "r", encoding="utf-8") as f:
    musculos_data = json.load(f)

# ==========================================
# GENERADORES DE TEXTO NATURAL
# ==========================================

def saludar_usuario():
    saludos = [
        "¡Buenas! ¿Qué tal ese cuerpo? Dime, ¿qué quieres entrenar hoy?",
        "¡Hola! Aquí estoy listo para echarte una mano con la rutina. ¿Qué necesitas saber?",
        "¡Ey! Vamos a ver cómo mejorar ese físico. ¿Tienes dudas con algún ejercicio?",
    ]
    return random.choice(saludos)

def despedir_usuario():
    despedidas = [
        "¡Venga, a darle duro! Si te surgen más dudas, aquí estaré.",
        "¡Buen entreno! Recuerda descansar bien, que ahí es donde se crece.",
        "¡Nos vemos! Cuida la técnica y mete peso con cabeza.",
    ]
    return random.choice(despedidas)

def no_entender():
    return (
        "Mmm, no estoy seguro de haberte entendido bien. Háblame como si estuviéramos en el gym. "
        "Pregúntame cosas como '¿Cómo entreno el pecho?', 'Explícame el press banca' o 'Diferencias entre sentadilla y prensa'. "
        "¡Inténtalo de nuevo!"
    )

# ==========================================
# FUNCIONES DE MÚSCULOS (Estilo Conversacional)
# ==========================================

def explicar_musculo(nombre_musculo):
    musculo = next((m for m in musculos_data if m['nombre'].lower() == nombre_musculo.lower()), None)
    
    if not musculo:
        return f"Oye, pues no me suena el músculo '{nombre_musculo}'. A lo mejor lo conozco por su nombre técnico, ¿puedes probar de otra forma?"

    # Construcción narrativa
    texto = (
        f"Hablemos del **{musculo['nombre']}**. Es un músculo fundamental que tienes ubicado en la {musculo['localizacion'].lower()}. "
        f"Su función principal es clara: se encarga de {musculo['funcion'].lower()}. "
        f"Al ser un grupo {musculo['grupo_muscular'].lower()} del tren {musculo['tren'].lower()}, juega un papel clave en tu físico.\n\n"
    )

    if "subdivisiones" in musculo:
        partes = ", ".join(musculo['subdivisiones'])
        texto += (
            f"Una cosa importante es que no es una pieza única; se divide anatómicamente en varias partes: **{partes}**. "
            "Es bueno saberlo para atacarlo desde distintos ángulos.\n\n"
        )

    ejercicios_relacionados = [
        e['nombre_agrupado'] for e in ejercicios_data 
        if e['musculo_objetivo'] == musculo['id']
    ]

    if ejercicios_relacionados:
        top_ejercicios = ", ".join(ejercicios_relacionados[:4])
        texto += f"Si quieres desarrollarlo, mis ejercicios favoritos para empezar serían: **{top_ejercicios}**, entre otros."
    else:
        texto += "Ahora mismo no tengo ejercicios específicos listados para este, pero cualquier movimiento que replique su función te servirá."

    return texto


def explicar_porcion_muscular(nombre_musculo, porcion_clave):
    musculo = next((m for m in musculos_data if m['nombre'].lower() == nombre_musculo.lower()), None)
    if not musculo:
        return f"No encuentro el músculo '{nombre_musculo}' en mi base de datos."

    recomendaciones = []
    ejercicios_musculo = [e for e in ejercicios_data if e['musculo_objetivo'] == musculo['id']]
    
    for ej in ejercicios_musculo:
        for var in ej['variantes']:
            if porcion_clave.lower() in var['enfoque'].lower():
                recomendaciones.append(f"- Con el **{ej['nombre_agrupado']}** (usando {var['equipo']}), ya que {var['enfoque'].lower()}.")

    if not recomendaciones:
        return (f"Verás, el {nombre_musculo} tiene esa parte, pero ahora mismo no tengo un ejercicio etiquetado *exclusivamente* "
                f"para la zona '{porcion_clave}'. Lo mejor es que hagas los ejercicios básicos del músculo general.")

    texto = (
        f"¡Buena pregunta! Muchos se olvidan de los detalles. Si quieres enfatizar concretamente la parte **{porcion_clave}** "
        f"del {nombre_musculo}, te sugiero lo siguiente:\n\n"
        + "\n".join(recomendaciones) + "\n\n"
        "Prueba a meter estos en tu rutina y notarás la diferencia en esa zona."
    )
    return texto


def comparar_musculos(nombre1, nombre2):
    m1 = next((m for m in musculos_data if m['nombre'].lower() == nombre1.lower()), None)
    m2 = next((m for m in musculos_data if m['nombre'].lower() == nombre2.lower()), None)

    if not m1 or not m2:
        return "Me falta información sobre uno de esos dos músculos para poder compararlos bien."

    relacion = "pertenecen al mismo tren" if m1['tren'] == m2['tren'] else "están en zonas opuestas del cuerpo"
    
    texto = (
        f"Vamos a ver las diferencias entre el **{m1['nombre']}** y el **{m2['nombre']}**.\n\n"
        f"Por un lado tienes el **{m1['nombre']}**, que es un músculo {m1['grupo_muscular'].lower()} diseñado para {m1['funcion'].lower()}. "
        f"En cambio, el **{m2['nombre']}** es {m2['grupo_muscular'].lower()} y su trabajo es {m2['funcion'].lower()}.\n\n"
        f"Básicamente, {relacion}. "
    )

    if m1['tren'] == m2['tren']:
         texto += "Es probable que puedas trabajarlos en la misma sesión si haces una rutina dividida por zonas."
    
    return texto

# ==========================================
# FUNCIONES DE EJERCICIOS (Estilo Conversacional)
# ==========================================

def explicar_ejercicio(nombre_ejercicio):
    ejercicio = next((e for e in ejercicios_data if e['nombre_agrupado'].lower() == nombre_ejercicio.lower()), None)
    
    if not ejercicio:
        return f"No me suena el ejercicio '{nombre_ejercicio}'. ¿Quizás tiene otro nombre o es una variante muy específica?"

    # Convertir lista de variantes en texto fluido
    variantes_texto = []
    for v in ejercicio['variantes']:
        variantes_texto.append(f"con **{v['equipo']}** (ideal para {v['enfoque'].lower()})")
    
    lista_variantes = "; ".join(variantes_texto)

    texto = (
        f"El **{ejercicio['nombre_agrupado']}** es un clásico. Se trata de un ejercicio de tipo **{ejercicio['tipo'].lower()}** "
        f"que va directo al {ejercicio['musculo_objetivo']}. \n\n"
        f"La idea básica es esta: {ejercicio['descripcion_general'].lower()} \n\n"
        f"Lo bueno es que no tienes una sola forma de hacerlo. Puedes probar {lista_variantes}. "
        "Dependiendo de qué material tengas a mano o qué busques, elige una u otra."
    )
    return texto


def explicar_variante_ejercicio(nombre_ejercicio, equipo_variante):
    ejercicio = next((e for e in ejercicios_data if e['nombre_agrupado'].lower() == nombre_ejercicio.lower()), None)
    
    if not ejercicio:
        return "Primero necesito encontrar el ejercicio base, y ese nombre no me sale."

    variante = next((v for v in ejercicio['variantes'] if v['equipo'].lower() == equipo_variante.lower()), None)
    
    if not variante:
        return f"Para el {ejercicio['nombre_agrupado']} no tengo registrada esa variante exacta. Intenta con Barra, Mancuernas o Máquina."

    return (
        f"Si decides hacer **{ejercicio['nombre_agrupado']}** usando **{variante['equipo']}**, estás tomando una buena decisión si buscas {variante['enfoque'].lower()}.\n\n"
        f"Un consejo profesional para sacarle partido: {variante['tip_clave'].lower()} ¡Pruébalo así la próxima vez!"
    )


def comparar_ejercicios(nombre1, nombre2):
    e1 = next((e for e in ejercicios_data if e['nombre_agrupado'].lower() == nombre1.lower()), None)
    e2 = next((e for e in ejercicios_data if e['nombre_agrupado'].lower() == nombre2.lower()), None)

    if not e1 or not e2:
        return "Me falta info de alguno de esos ejercicios para poder compararlos."

    # Lógica conversacional
    texto = f"Es una comparación interesante: **{e1['nombre_agrupado']}** contra **{e2['nombre_agrupado']}**.\n\n"
    
    if e1['musculo_objetivo'] == e2['musculo_objetivo']:
        texto += f"Ambos van a por el mismo objetivo: el **{e1['musculo_objetivo']}**. "
    else:
        texto += f"Son muy distintos: el primero es para **{e1['musculo_objetivo']}** y el segundo para **{e2['musculo_objetivo']}**. "

    texto += f"El {e1['nombre_agrupado']} es un movimiento {e1['tipo'].lower()}, mientras que el {e2['nombre_agrupado']} es {e2['tipo'].lower()}.\n\n"

    # Recomendación de orden
    if e1['tipo'] == "Compuesto" and e2['tipo'] == "Aislamiento":
        texto += (
            "Si vas a meter los dos en tu rutina, mi consejo es claro: **haz primero el Compuesto** (el primero) cuando estás fresco "
            "para mover kilos, y deja el de Aislamiento para rematar al final."
        )
    elif e2['tipo'] == "Compuesto" and e1['tipo'] == "Aislamiento":
        texto += (
            "En tu rutina, **deberías priorizar el segundo ejercicio** al principio, ya que es el compuesto pesado, "
            "y usar el primero más tarde para bombear y detallar."
        )
    else:
        texto += "Como tienen una naturaleza similar, puedes alternarlos o elegir el que más te guste según cómo te sientas hoy."

    return texto


def sugerir_ejercicios(musculo_objetivo, tipo="Compuesto"):
    m_obj = next((m for m in musculos_data if m['nombre'].lower() == musculo_objetivo.lower()), None)
    id_busqueda = m_obj['id'] if m_obj else musculo_objetivo.lower()

    encontrados = [
        e for e in ejercicios_data 
        if e['musculo_objetivo'] == id_busqueda and e['tipo'].lower() == tipo.lower()
    ]

    if not encontrados:
        return f"Pues mira, no he encontrado ejercicios de tipo '{tipo}' específicamente para {musculo_objetivo}. A lo mejor deberíamos probar otro enfoque."

    # Formato lista natural
    nombres = [e['nombre_agrupado'] for e in encontrados]
    
    if len(nombres) > 1:
        lista_str = ", ".join(nombres[:-1]) + " y " + nombres[-1]
    else:
        lista_str = nombres[0]

    return (
        f"Si quieres darle caña al **{musculo_objetivo}** con ejercicios **{tipo.lower()}s**, tienes buenas opciones. "
        f"Yo te recomendaría probar con: **{lista_str}**. ¡Son mano de santo!"
    )


# ==========================================
# GESTOR CENTRAL
# ==========================================
def devolver_mensaje(funcion, argumentos):
    mapa_funciones = {
        "saludar": saludar_usuario,
        "despedir": despedir_usuario,
        "no entender": no_entender,
        "explicar musculo": explicar_musculo,
        "explicar porcion": explicar_porcion_muscular,
        "comparar musculos": comparar_musculos,
        "explicar ejercicio": explicar_ejercicio,
        "explicar variante": explicar_variante_ejercicio,
        "comparar ejercicios": comparar_ejercicios,
        "recomendar ejercicio": sugerir_ejercicios
    }

    if funcion in mapa_funciones:
        try:
            if argumentos:
                return mapa_funciones[funcion](*argumentos)
            else:
                return mapa_funciones[funcion]()
        except TypeError:
             return "¡Ups! Me has dado un número de argumentos incorrecto para esa pregunta. Inténtalo de nuevo."
    
    return f"Vaya, esa función '{funcion}' no me suena de nada."



# ==========================================
# BLOQUE MAIN DE PRUEBAS (Test de Personalidad)
# ==========================================
if __name__ == "__main__":
    import time

    def imprimir_test(titulo, funcion, args):
        print(f"\n{'='*60}")
        print(f"🧪 TEST: {titulo}")
        print(f"❓ Input: {funcion} -> {args}")
        print(f"{'-'*60}")
        respuesta = devolver_mensaje(funcion, args)
        print(f"🤖 BOT:\n{respuesta}")
        print(f"{'='*60}\n")
        time.sleep(1) # Pequeña pausa para leer mejor en consola

    print("🚀 INICIANDO BATERÍA DE PRUEBAS DE FITNESS BOT 🚀")

    # 1. PRUEBA DE SALUDO
    imprimir_test("Saludo Inicial", "saludar", [])

    # 2. PRUEBA DE MÚSCULO GRANDE (CON SUBDIVISIONES)
    imprimir_test("Explicar Pectoral", "explicar musculo", ["Pectoral"])

    # 3. PRUEBA DE MÚSCULO PEQUEÑO
    imprimir_test("Explicar Bíceps", "explicar musculo", ["Bíceps"])

    # 4. PRUEBA DE PORCIÓN ESPECÍFICA (Detalle técnico)
    # Probamos si detecta la "Cabeza Lateral" del Tríceps
    imprimir_test("Explicar Porción (Tríceps Lateral)", "explicar porcion", ["Tríceps", "Cabeza Lateral (Externa)"])

    # 5. PRUEBA DE EJERCICIO AGRUPADO (Press Banca)
    imprimir_test("Explicar Press Banca", "explicar ejercicio", ["Press de Banca Plano"])

    # 6. PRUEBA DE VARIANTE ESPECÍFICA (Diferencia entre Barra y Mancuerna)
    imprimir_test("Explicar Variante (Banca con Mancuernas)", "explicar variante", ["Press de Banca Plano", "Mancuernas"])

    # 7. COMPARACIÓN DE EJERCICIOS (Lógica de Rutina)
    # Compuesto (Sentadilla) vs Aislamiento (Extensión) -> Debería sugerir primero la Sentadilla
    imprimir_test("Comparar Squat vs Extensión", "comparar ejercicios", ["Sentadilla (Squat)", "Extensión de Rodilla"])

    # 8. COMPARACIÓN DE MÚSCULOS (Antagonistas)
    imprimir_test("Comparar Pecho vs Espalda", "comparar musculos", ["Pectoral", "Dorsal Ancho"])

    # 9. RECOMENDACIÓN (Filtro por tipo)
    imprimir_test("Sugerir Ejercicios Compuestos para Pierna", "recomendar ejercicio", ["Cuádriceps", "Compuesto"])

    # 10. ERROR INTENCIONADO (Para ver cómo maneja fallos)
    imprimir_test("Prueba de Error (Músculo inexistente)", "explicar musculo", ["Músculo Inventado"])

    print("🏁 PRUEBAS FINALIZADAS 🏁")