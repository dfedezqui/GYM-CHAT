# Cargar datos
import json
import os


base_path = os.path.join(os.path.dirname(__file__), "database")
with open(os.path.join(base_path, "ejercicios.json"), "r", encoding="utf-8") as f:
    ejercicios_data = json.load(f)
with open(os.path.join(base_path, "musculos.json"), "r", encoding="utf-8") as f:
    musculos_data = json.load(f)
    

import random

def saludar_usuario():
    saludos = [
        "¡Hola! ¿Listo para entrenar?",
        "¡Bienvenido! ¿En qué puedo ayudarte con tu entrenamiento hoy?",
        "¡Hola atleta! ¿Quieres mejorar fuerza, hipertrofia o aprender algo nuevo?",
        "¡Ey! Aquí estoy para ayudarte con rutinas, ejercicios o dudas musculares."
    ]
    return random.choice(saludos)


def despedir_usuario():
    despedidas = [
        "¡Buen trabajo! Recuerda que la constancia vence al talento 💪",
        "¡Hasta la próxima! Mantente fuerte y enfocado.",
        "¡Nos vemos pronto! Sigue progresando y cuidando tu forma.",
        "¡Cuídate! Estoy aquí cuando necesites más ayuda o motivación.",
        "¡Adiós! Recuerda al fallo o muere flaco.",
    ]
    return random.choice(despedidas)

def responder_duda_general(texto_usuario):
        return (
            "Puedo ayudarte con los músculos y ejercicios de forma natural. 💪\n"
            "Por ejemplo, puedes pedirme que:\n"
            "- Te explique un ejercicio o un músculo\n"
            "- Compare dos ejercicios o dos músculos\n"
            "- Te sugiera ejercicios según el músculo y el objetivo (fuerza o hipertrofia)\n"
            "- Describa variantes o porciones musculares\n"
            "- O simplemente resolver una duda general que tengas\n\n"
            "¡Tú dime y empezamos! 🔍"
        )

def explicar_musculo(nombre_musculo):
    """
    Busca y explica la información de un músculo dado su nombre.

    Parámetros:
    nombre_musculo (str): Nombre del músculo que se quiere consultar.

    Retorna:
    str: Texto descriptivo con la ubicación, función y segmentos musculares, 
         incluyendo ejercicios para cada segmento. Si no se encuentra el músculo,
         devuelve un mensaje indicando que no se encontró información.
    """ 

    musculo = next((m for m in musculos_data if m['Nombre'].lower() == nombre_musculo.lower()), None)
    if not musculo:
        return f"Oh mi gymbro, no he podido encontrar información acerca de '{nombre_musculo}', ¿Te puede ayudar con otro musculo?."

    texto = (
        f"El {musculo['Nombre']} es un músculo que está ubicado en {musculo['Localizacion'].lower()}. "
        f"Su función principal {musculo['Funcion'].lower()}.\n\n"
    )

    tamano = musculo.get("Tamanio", musculo.get("Tamaño", "desconocido")).lower()
    sinergistas = musculo.get("Sinergistas", musculo.get("Sinergia", []))
    if isinstance(sinergistas, str):  # Por si está como cadena en lugar de lista
        sinergistas = [sinergistas]
    sinergia_str = ", ".join(sinergistas).lower() if sinergistas else "ningún músculo sinérgico"

    if tamano == "grande":
        recuperacion = "72 h"
        recomendacion = "principal"
    elif tamano == "mediano":
        recuperacion = "48 h"
        recomendacion = "secundario"
    elif tamano == "pequeño":
        recuperacion = "24 h"
        recomendacion = "secundario"
    else:
        recuperacion = "desconocido"
        recomendacion = "secundario"

    texto += (
        f"Al ser un músculo {tamano}, se recomienda entrenarlo de forma {recomendacion} "
        f"junto a los músculos sinérgicos: {sinergia_str}. "
        f"Este músculo suele necesitar aproximadamente {recuperacion} para recuperarse completamente.\n\n"
        "Cuenta con varios segmentos, los cuales se pueden entrenar con ejercicios enfocados en su zona particular:\n\n"
    )

    segmentos = musculo.get('Segmentos_musculares', [])
    for i, segmento in enumerate(segmentos, start=1):
        ejercicios = ", ".join(segmento.get('Ejercicios', []))
        texto += (
            f"{i}. {segmento['Nombre']}:\n"
            f"   Se localiza en {segmento['Localizacion'].lower()} y se puede trabajar con ejercicios como {ejercicios}.\n\n"
        )
    return texto



def explicar_porcion_muscular(nombre_musculo, porcion):
    """
    Devuelve una explicación específica de una porción de un músculo.

    Parámetros:
    nombre_musculo (str): Nombre del músculo principal.
    porcion (str): Nombre del segmento muscular específico.

    Retorna:
    str: Descripción de la porción y ejercicios recomendados.
    """
    musculo = next((m for m in musculos_data if m['Nombre'].lower() == nombre_musculo.lower()), None)
    if not musculo:
        return f"No se encontró el músculo '{nombre_musculo}'. ¿Podrías verificar el nombre?"

    segmentos = musculo.get("Segmentos_musculares", [])
    segmento = next((s for s in segmentos if s["Nombre"].lower() == porcion.lower()), None)
    if not segmento:
        return f"No se encontró la porción '{porcion}' dentro del músculo '{nombre_musculo}'. ¿Podrías verificar el nombre?"

    # Ejercicios específicos del segmento
    ejercicios_principales = ", ".join(segmento.get("Ejercicios", []))

    # Ejercicios de otras porciones (actúa secundariamente)
    ejercicios_secundarios = []
    for s in segmentos:
        if s["Nombre"].lower() != porcion.lower():
            ejercicios_secundarios.extend(s.get("Ejercicios", []))

    ejercicios_secundarios_texto = ", ".join(ejercicios_secundarios)

    return (
        f"El músculo {porcion} pertenece al {nombre_musculo}, se localiza en {segmento['Localizacion'].lower()}.\n\n"
        f"Actúa también de forma secundaria en ejercicios como: {ejercicios_secundarios_texto}.\n\n"
        f"Sin embargo, si quieres enfocarte específicamente en esta porción, los mejores ejercicios son: {ejercicios_principales}."
    )

def comparar_musculos(nombre1, nombre2):
    """
    Compara dos músculos: ubicación, función, tamaño, sinergia y ejercicios.

    Parámetros:
    nombre1 (str): Primer músculo.
    nombre2 (str): Segundo músculo.

    Retorna:
    str: Comparación entre ambos músculos con contexto anatómico y recomendaciones.
    """

    # Buscar músculos en los datos
    musculo1 = next((m for m in musculos_data if m['Nombre'].lower() == nombre1.lower()), None)
    musculo2 = next((m for m in musculos_data if m['Nombre'].lower() == nombre2.lower()), None)

    if not musculo1 or not musculo2:
        faltantes = []
        if not musculo1:
            faltantes.append(nombre1)
        if not musculo2:
            faltantes.append(nombre2)
        return f"No se encontró información sobre: {', '.join(faltantes)}"

    tren1 = musculo1.get("Tren", "desconocido").lower()
    tren2 = musculo2.get("Tren", "desconocido").lower()
    tam1 = musculo1.get("Tamaño", "desconocido").lower()
    tam2 = musculo2.get("Tamaño", "desconocido").lower()

    sinergistas1 = [s.lower() for s in musculo1.get("Sinergia", "").split(",")] if isinstance(musculo1.get("Sinergia"), str) else []
    sinergistas2 = [s.lower() for s in musculo2.get("Sinergia", "").split(",")] if isinstance(musculo2.get("Sinergia"), str) else []

    nombre1_lower = musculo1["Nombre"].lower()
    nombre2_lower = musculo2["Nombre"].lower()

    # Comprobar sinergia mutua
    sinergia = (nombre2_lower in sinergistas1) or (nombre1_lower in sinergistas2)

    # Introducción contextual
    intro = ""
    if tren1 == tren2:
        intro += f"Ambos músculos pertenecen al tren {tren1} del cuerpo.\n"
    else:
        intro += f"{nombre1} pertenece al tren {tren1}, mientras que {nombre2} está en el tren {tren2}.\n"

    intro += f"{nombre1} es un músculo {tam1}, y {nombre2} es un músculo {tam2}.\n"

    if sinergia:
        intro += (
            f"Además, estos músculos suelen trabajar juntos en movimientos compuestos. "
            f"Por ejemplo, el {nombre1} y el {nombre2} pueden colaborar en ejercicios combinados. "
            f"💡 Se recomienda entrenarlos en la misma sesión si buscas sinergia muscular.\n\n"
        )
    else:
        intro += (
            f"No tienen una relación sinérgica directa habitual, pero pueden combinarse según el enfoque de tu rutina.\n\n"
        )

    def resumen_musculo(m):
        segmentos = ", ".join(seg['Nombre'] for seg in m.get('Segmentos_musculares', []))
        ejercicios = []
        for seg in m.get('Segmentos_musculares', []):
            ejercicios += seg.get('Ejercicios', [])
        ejercicios_unicos = ", ".join(sorted(set(ejercicios)))
        return (
            f"- Ubicación: {m['Localizacion']}\n"
            f"- Función principal: {m['Funcion']}\n"
            f"- Segmentos: {segmentos}\n"
            f"- Ejercicios comunes: {ejercicios_unicos}"
        )

    comparacion = (
        f"📌 {nombre1}:\n{resumen_musculo(musculo1)}\n\n"
        f"📌 {nombre2}:\n{resumen_musculo(musculo2)}"
    )

    return f"Comparación entre {nombre1} y {nombre2}:\n\n{intro}{comparacion}"
    

def explicar_ejercicio(nombre_ejercicio):
    """
    Busca y explica la información de un ejercicio dado su nombre.

    Parámetros:
    nombre_ejercicio (str): Nombre del ejercicio que se quiere consultar.

    Retorna:
    str: Texto descriptivo con músculos principales y secundarios involucrados, 
         la ejecución del ejercicio, variantes con descripción y sus puntos fuertes y débiles,
         y sugerencia sobre su orden en la rutina y tipo de estímulo.
    """

    ejercicio = next((e for e in ejercicios_data if e['Nombre'].lower() == nombre_ejercicio.lower()), None)
    if not ejercicio:
        return f"Perdona, no encontré información sobre '{nombre_ejercicio}'. ¿Quieres que te ayude con otro ejercicio?"

    tipo_estimulo = ejercicio.get("Tipo_de_estímulo", "No especificado")

    if tipo_estimulo == "Fuerza":
        sugerencia_orden = "como primer o segundo ejercicio de tu rutina, para aprovechar mayor energía y rendimiento"
    elif tipo_estimulo == "Hipertrofia":
        sugerencia_orden = "en la segunda mitad o al final de tu rutina, cuando busques fatigar y aislar el músculo"
    else:
        sugerencia_orden = "en la parte de la rutina que mejor se ajuste a tus objetivos"

    texto = (
        f"El {ejercicio['Nombre']} es un ejercicio que se enfoca principalmente en el {ejercicio['Musculo_principal_concreto'].lower()}, "
        f"que forma parte del grupo muscular del {ejercicio['Musculo_principal'].lower()}.\n\n"
        f"Además, este ejercicio también trabaja músculos secundarios como {', '.join(ejercicio['Musculos_secundarios_concretos']).lower()}.\n\n"
        f"Para realizarlo correctamente, debes {ejercicio['Ejecucion'].lower()}\n\n"
        f"Este ejercicio se clasifica como un ejercicio de *{tipo_estimulo.lower()}*, "
        f"por lo que se recomienda incluirlo {sugerencia_orden}.\n\n"
        "Entre sus variantes principales destacan:\n\n"
    )

    variantes = ejercicio.get('Variantes', [])
    for i, variante in enumerate(variantes, start=1):
        texto += (
            f"{i}. Tipo: {variante['Tipo']}\n"
            f"   Esta variante se caracteriza por {variante['Descripcion'].lower()}\n"
            f"   Entre sus puntos fuertes destaca que {variante['Puntos_fuertes'].lower()}\n"
            f"   Sin embargo, presenta como desventaja que {variante['Puntos_debiles'].lower()}\n\n"
        )

    return texto

def explicar_variante_ejercicio(nombre_ejercicio, tipo_variante):
    """
    Devuelve una explicación específica de una variante de un ejercicio.

    Parámetros:
    nombre_ejercicio (str): Nombre del ejercicio principal.
    tipo_variante (str): Tipo de variante (ej. "Máquina", "Mancuernas", "Polea").

    Retorna:
    str: Descripción detallada de la variante, ventajas, desventajas y cuándo usarla.
    """

    ejercicio = next((e for e in ejercicios_data if e['Nombre'].lower() == nombre_ejercicio.lower()), None)
    if not ejercicio:
        return f"No se encontró el ejercicio '{nombre_ejercicio}'. ¿Puedes verificar el nombre?"

    variantes = ejercicio.get("Variantes", [])
    variante = next((v for v in variantes if v["Tipo"].lower() == tipo_variante.lower()), None)
    if not variante:
        return f"No se encontró la variante '{tipo_variante}' para el ejercicio '{nombre_ejercicio}'. ¿Puedes verificar el tipo?"

    descripcion = variante.get("Descripcion", "Sin descripción.")
    puntos_fuertes = variante.get("Puntos_fuertes", "No especificados.")
    puntos_debiles = variante.get("Puntos_debiles", "No especificados.")
    recomendacion = variante.get("Cuando_recomendarla", "Puedes incluirla según tu objetivo o disponibilidad de equipo.")

    return (
        f"La variante **{tipo_variante}** del ejercicio **{nombre_ejercicio}** se caracteriza por:\n\n"
        f"📌 **Descripción:** {descripcion}\n"
        f"✅ **Puntos fuertes:** {puntos_fuertes}\n"
        f"⚠️ **Puntos débiles:** {puntos_debiles}\n\n"
        f"🗓️ **¿Cuándo usarla?** {recomendacion}"
    )



def comparar_ejercicios(nombre1, nombre2):
    """
    Compara dos ejercicios: músculos involucrados, sinergia, orden sugerido y variantes.

    Parámetros:
    nombre1 (str): Nombre del primer ejercicio.
    nombre2 (str): Nombre del segundo ejercicio.

    Retorna:
    str: Comparación descriptiva entre ambos ejercicios con recomendaciones prácticas.
    """

    ej1 = next((e for e in ejercicios_data if e['Nombre'].lower() == nombre1.lower()), None)
    ej2 = next((e for e in ejercicios_data if e['Nombre'].lower() == nombre2.lower()), None)

    if not ej1 or not ej2:
        faltantes = []
        if not ej1:
            faltantes.append(nombre1)
        if not ej2:
            faltantes.append(nombre2)
        return f"No se encontró información sobre: {', '.join(faltantes)}"

    # Grupo muscular principal
    musc1 = ej1["Musculo_principal"]
    musc2 = ej2["Musculo_principal"]

    # Evaluar sinergia
    sinergicos = False
    principal1 = ej1["Musculo_principal_concreto"].lower()
    principal2 = ej2["Musculo_principal_concreto"].lower()
    secundarios1 = [m.lower() for m in ej1.get("Musculos_secundarios_concretos", [])]
    secundarios2 = [m.lower() for m in ej2.get("Musculos_secundarios_concretos", [])]

    if (principal1 in secundarios2) or (principal2 in secundarios1) or (principal1 == principal2):
        sinergicos = True

    # Estímulo y orden
    tipo1 = ej1.get("Tipo_de_estímulo", "No especificado")
    tipo2 = ej2.get("Tipo_de_estímulo", "No especificado")

    if tipo1 == "Fuerza" and tipo2 == "Hipertrofia":
        orden = f"Para una rutina óptima, realiza primero **{ej1['Nombre']}** (fuerza) y luego **{ej2['Nombre']}** (hipertrofia)."
    elif tipo2 == "Fuerza" and tipo1 == "Hipertrofia":
        orden = f"Para una rutina óptima, realiza primero **{ej2['Nombre']}** (fuerza) y luego **{ej1['Nombre']}** (hipertrofia)."
    else:
        orden = f"Ambos ejercicios tienen un enfoque similar ({tipo1.lower()}), puedes alternarlos según tu fatiga o preferencias."

    # Texto introductorio
    texto = (
        f"🔍 Comparativa entre **{ej1['Nombre']}** y **{ej2['Nombre']}**:\n\n"
        f"- **{ej1['Nombre']}** trabaja principalmente el **{ej1['Musculo_principal_concreto']}** del grupo **{musc1}**.\n"
        f"- **{ej2['Nombre']}** se enfoca en el **{ej2['Musculo_principal_concreto']}** del grupo **{musc2}**.\n\n"
    )

    if sinergicos:
        texto += "✅ *Estos ejercicios tienen sinergia*, ya que comparten músculos principales o secundarios, por lo que pueden complementarse bien en la misma rutina.\n\n"
    else:
        texto += "ℹ️ *No presentan sinergia directa*, pero pueden combinarse si se quiere un trabajo completo o por contraste.\n\n"

    texto += f"⚖️ {orden}\n\n"

    # Esquema de comparación
    def resumen_ejercicio(e):
        secundarios = ", ".join(e.get("Musculos_secundarios_concretos", []))
        variantes = "\n".join(
            [f"  - {v['Tipo']}: {v['Descripcion']}" for v in e.get("Variantes", [])]
        )
        return f"🎯 Músculos secundarios: {secundarios}\n🧩 Variantes:\n{variantes}"

    esquema = (
        f"📌 **{ej1['Nombre']}**\n"
        f"{resumen_ejercicio(ej1)}\n\n"
        f"📌 **{ej2['Nombre']}**\n"
        f"{resumen_ejercicio(ej2)}"
    )

    return texto + esquema

def sugerir_ejercicios(musculo, objetivo="hipertrofia"):
    """
    Sugiere ejercicios según el grupo muscular principal y el tipo de estímulo deseado.

    Parámetros:
    musculo (str): Grupo muscular principal (ej. "Pectoral", "Bíceps", "Glúteo").
    objetivo (str): Tipo de estímulo: "fuerza" o "hipertrofia".

    Retorna:
    str: Lista de ejercicios recomendados para ese músculo y objetivo.
    """

    objetivo = objetivo.lower()
    if objetivo not in ["fuerza", "hipertrofia"]:
        return "El objetivo debe ser 'fuerza' o 'hipertrofia'."

    encontrados = [
        e for e in ejercicios_data
        if e["Musculo_principal"].lower() == musculo.lower()
        and e.get("Tipo_de_estímulo", "").lower() == objetivo
    ]

    if not encontrados:
        return f"No se encontraron ejercicios para el músculo '{musculo}' con objetivo '{objetivo}'."

    respuesta = (
        f"🎯 Ejercicios para **{musculo}** orientados a **{objetivo}**:\n\n"
    )
    for e in encontrados:
        respuesta += f"• {e['Nombre']}: trabaja principalmente el {e['Musculo_principal_concreto'].lower()}\n"

    return respuesta

