
# Cargar datos
import json
import os


base_path = os.path.join(os.path.dirname(__file__), "database")
with open(os.path.join(base_path, "ejercicios.json"), "r", encoding="utf-8") as f:
    ejercicios_data = json.load(f)
with open(os.path.join(base_path, "musculos.json"), "r", encoding="utf-8") as f:
    musculos_data = json.load(f)
    



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
    f"El {musculo['Nombre']} es un musculo que está ubicado en {musculo['Localizacion'].lower()}. "
    f"Su función principal {musculo['Funcion'].lower()}.\n\n"
    "Cuenta con varios segmentos, los cuales se pueden entrenar con ejercicios enfocados en su zona particular:\n\n"
    )   
    
    segmentos = musculo.get('Segmentos_musculares', [])
    for i, segmento in enumerate(segmentos, start=1):
        ejercicios = ", ".join(segmento.get('Ejercicios', []))
        texto += (
            f"{i}. **{segmento['Nombre']}**:\n"
            f"   Se localiza en {segmento['Localizacion'].lower()} y se puede trabajar con ejercicios como {ejercicios}.\n\n"
        )
    return texto


def explicar_ejercicio(nombre_ejercicio):
    """
    Busca y explica la información de un ejercicio dado su nombre.

    Parámetros:
    nombre_ejercicio (str): Nombre del ejercicio que se quiere consultar.

    Retorna:
    str: Texto descriptivo con músculos principales y secundarios involucrados, 
         la ejecución del ejercicio, variantes con descripción y sus puntos fuertes y débiles,
         y recomendación de orden para incluirlo en la rutina. Si no se encuentra el ejercicio,
         devuelve un mensaje indicando que no se encontró información.
    """
     
    ejercicio = next((e for e in ejercicios_data if e['Nombre'].lower() == nombre_ejercicio.lower()), None)
    if not ejercicio:
        return f"Perdona, no encontré información sobre '{nombre_ejercicio}'. ¿Quieres que te ayude con otro ejercicio?"

    texto = (
        f"El {ejercicio['Nombre']} es un ejercicio que se enfoca principalmente en el {ejercicio['Musculo_principal_concreto'].lower()}, "
        f"que forma parte del grupo muscular del {ejercicio['Musculo_principal'].lower()}.\n\n"
        f"Además, este ejercicio también trabaja músculos secundarios como {', '.join(ejercicio['Musculos_secundarios_concretos']).lower()}.\n\n"
        f"Para realizarlo correctamente, debes {ejercicio['Ejecucion'].lower()}\n\n"
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
    texto += f"Este ejercicio te {ejercicio.get('Recomendacion_de_orden', 'No disponible').lower()}."

    return texto




def main():
    # Ejemplo de uso
    opcion = input("¿Qué quieres hacer? (m/e): ").strip().lower()
    if opcion == "m":
        nombre = input("Escribe el nombre del músculo: ").strip()
        print(explicar_musculo(nombre))
    elif opcion == "e":
        nombre = input("Escribe el nombre del ejercicio: ").strip()
        print(explicar_ejercicio(nombre))
    else:
        print("Opción no válida. Por favor, elige 'musculo(m)' o 'ejercicio(e)'.")

    
if __name__ == "__main__":
    main()



