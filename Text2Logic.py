import re # Importa el módulo para el manejo de expresiones regulares.
import textwrap # Importa el módulo para el formateo de texto.
import os

def centrar_texto_en_pantalla(texto):
    espacios_en_blanco = int((os.get_terminal_size().columns - len(texto)) / 2)
    print(' ' * espacios_en_blanco + texto)

def imprimir_nombre_del_juego(): # Función que muestra el nombre del juego
    centrar_texto_en_pantalla("-------------------")
    centrar_texto_en_pantalla("|                 |")
    centrar_texto_en_pantalla("|   TEXT2LOGIC    |")
    centrar_texto_en_pantalla("|                 |")
    centrar_texto_en_pantalla("-------------------")

# función que toma un resultado y una serie de patrones y devuelve una tupla con el 
# resultado y una lista de patrones modificados. Los patrones son expresiones en 
# lenguaje natural que se utilizarán para encontrar coincidencias en las oraciones.
def Regla(resultado, *patrones): 
    return (resultado, [nombre_grupo(pat) + '$' for pat in patrones]) 

# Una función que toma un patrón y modifica las llaves entre corchetes (por ejemplo, {P}) 
# en expresiones regulares con grupos con nombres. Esto se hace para capturar partes 
# específicas de las oraciones.
def nombre_grupo(pat):
    return re.sub('{(.)}', r'(?P<\1>.+?)', pat)

# Una función que toma una palabra y la envuelve con \b, que representa límites de palabra 
# en una expresión regular.
def palabra(w):
    return r'\b' + w + r'\b'

# Se definen una serie de reglas que representan transformaciones de lenguaje natural a 
# lógica. Por ejemplo, "si {P} entonces {Q}" se convierte en "{P} ⇒ {Q}".
Regla('{P} ⇒ {Q}', 'si {P} entonces {Q}', 'si {P}, {Q}'),
reglas = [
    Regla('{P} ⇒ {Q}',         'si {P} entonces {Q}', 'si {P}, {Q}'),
    Regla('{P} ⋁ {Q}',          'ya sea {P} o {Q}', 'ya sea {P} o {Q}'),
    Regla('{P} ⋀ {Q}',          '{P} y {Q}'),
    Regla('～{P} ⋀ ～{Q}',       'ni {P} ni {Q}'),
    Regla('～{A}{P} ⋀ ～{A}{Q}', '{A} ni {P} ni {Q}'),
    Regla('～{Q} ⇒ {P}',        '{P} a menos que {Q}'),
    Regla('{P} ⇒ {Q}',          '{Q} siempre que {P}', '{Q} cada vez que {P}',
                               '{P} implica {Q}', '{P} por lo tanto {Q}',
                               '{Q}, si {P}', '{Q} si {P}', '{P} solo si {Q}'),
    Regla('{P} ⋀ {Q}',          '{P} y {Q}', '{P} pero {Q}'),
    Regla('{P} ⋁ {Q}',          '{P} o {Q}', '{P} o {Q}'),
    ]

# También se definen negaciones que permiten eliminar palabras como "no" de las oraciones.
negaciones = [
    (palabra("no"), ""),
    (palabra("no puede"), "puede"),
    (palabra("no puedo"), "puede"),
    (palabra("no va a"), "va a"),
    (palabra("no es"), "es"),
    ("n't", ""),
    ]

# Esta función toma una oración, una lista de reglas y definiciones y aplica las reglas a 
# la oración. Itera a través de las reglas y llama a aplicar_regla para intentar aplicar 
# cada regla a la oración. Si una regla se aplica, devuelve el resultado lógico.
def aplicar_reglas(oracion, reglas, definiciones):
    oracion = limpiar(oracion)
    for regla in reglas:
        resultado = aplicar_regla(oracion, regla, definiciones)
        if resultado:
            return resultado
    return aplicar_literal(oracion, negaciones, definiciones)

# Esta función toma una oración, una regla y definiciones y aplica la regla a la oración.
# Intenta encontrar una coincidencia entre la oración y los patrones de la regla utilizando 
# expresiones regulares. Si encuentra una coincidencia, captura los grupos definidos por 
# las expresiones regulares y llama a aplicar_reglas de manera recursiva para procesar las 
# partes capturadas.
def aplicar_regla(oracion, regla, definiciones):
    resultado, patrones = regla
    for pat in patrones:
        coincidencia = re.match(pat, oracion, flags=re.I)
        if coincidencia:
            grupos = coincidencia.groupdict()
            for P in sorted(grupos):
                grupos[P] = aplicar_reglas(grupos[P], reglas, definiciones)[0]
            return '(' + resultado.format(**grupos) + ')', definiciones

# Esta función toma una oración, una lista de negaciones y definiciones, y aplica las 
# negaciones a la oración. También asigna una polaridad (positiva o negativa) en función 
# de las negaciones aplicadas. Llama a nombre_proposicion para asignar un nombre único a 
# la oración procesada. Devuelve la oración procesada y las definiciones actualizadas.
def aplicar_literal(oracion, negaciones, definiciones):
    polaridad = ''
    for (neg, pos) in negaciones:
        (oracion, n) = re.subn(neg, pos, oracion, flags=re.I)
        polaridad += n * '～'
    oracion = limpiar(oracion)
    P = nombre_proposicion(oracion, definiciones)
    definiciones[P] = oracion
    return polaridad + P, definiciones

# Esta función toma una oración, definiciones y nombres predefinidos y asigna un nombre 
# único a la oración. Si la oración ya tiene una definición en el diccionario de 
# definiciones, utiliza ese nombre. Si no, asigna el próximo nombre disponible de la lista 
# de nombres.
def nombre_proposicion(oracion, definiciones, nombres='PQRSTUVWXYZBCDEFGHJKLMN'):
    invertido = {definiciones[P]: P for P in definiciones}
    if oracion in invertido:
        return invertido[oracion]
    else:
        return next(P for P in nombres if P not in definiciones)

# Esta función toma un texto y realiza algunas limpiezas, como eliminar espacios en 
# blanco adicionales, reemplazar apóstrofes con comillas simples y eliminar puntos y 
# comas al final.
def limpiar(texto):
    return ' '.join(texto.split()).replace("’", "'").rstrip('.').rstrip(',')

# Esta función toma una lista de oraciones y un ancho de línea como argumentos.
def logica(oraciones, ancho=80):
    for s in map(limpiar, oraciones):
        logica, definiciones = aplicar_reglas(s, reglas, {})
        print('\n' + textwrap.fill('Texto: ' + s +'.', ancho), '\n\nLógica:', logica)
        for P in sorted(definiciones):
            print('{}: {}'.format(P, definiciones[P]))

os.system('cls' if os.name == 'nt' else 'clear') # Se limpia la consola

# Oración para testing: Si tuvieran que justificarse ciertos hechos por su enorme tradición entonces, si estos hechos son inofensivos y respetan a todo ser viviente y al medio ambiente, no habría ningún problema
imprimir_nombre_del_juego()
oraciones = input("\nIngresa una o más oraciones en lenguaje natural, separadas por puntos: ").split('.')

os.system('cls' if os.name == 'nt' else 'clear') # Se limpia la consola
imprimir_nombre_del_juego()
print("\n")
logica(oraciones)

print("\n\n")