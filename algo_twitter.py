import os
import sys

DEFAULT_PARAM = 3

ERROR_IMPORTACION = (
    "El/los archivos a importar deben existir y ser .txt válidos"
)
DIRECCION_ERRONEA = "No se pudo exportar a esa dirección."
TOKENIZACION_INVALIDA = "El argumento de cantidad de tokens es inválido."
DB_INVALIDA = "Error al intentar abrir el programa."

CREAR = "1"
BUSCAR = "2"
ELIMINAR = "3"
IMPORTAR = "4"
EXPORTAR = "5"
SALIR = "6"
PEDIR_BUSQUEDA = "Ingrese la/s palabra/s clave a buscar:\n"
PEDIR_ELIMINACION = "Ingrese el tweet a eliminar:\n"
RESULTADOS_BUSQUEDA = "Resultados de la busqueda:"
SELECCION = "Seleccione una opcion:"
NO_ENCONTRADOS = "No se encontraron tweets."
TWEETS_ELIMINADOS_MENSAJE = "Tweets eliminados:"
NUMERO_INVALIDO = "Numero de tweet invalido."
INPUT_INVALIDO = "Input invalido."
ATRAS = "**"
FIN = "Finalizando..."
MENU = """Seleccione una opcion:

1. Crear Tweet
2. Buscar Tweet
3. Eliminar Tweet
4. Importar tweets
5. Exportar tweets
6. Salir
"""

DB_PATH = "db"


def main(args=["./algo_twitter.py", "3"]):
    """
    Funcion principal del programa.
    Ofrece las opciones hasta que se ingresa el numero 6.
    """
    tweets = {}
    tokens_ids = {}
    arg = validar_args(args)
    if not arg:
        print(TOKENIZACION_INVALIDA)
        return
    id = cargar_tweets(tweets, tokens_ids, arg)
    while True:
        opcion = input(MENU)
        if opcion == CREAR:
            tweet_y_normalizado = pedir_tweet()
            nuevo_tweet = crear_tweet(
                id, tweets, tokens_ids, arg, tweet_y_normalizado
            )
            if nuevo_tweet:
                agregar_a_db(id, nuevo_tweet)
                print(f"OK {id}")
                id += 1
            continue
        if opcion == BUSCAR:
            palabras_buscar = pedir_palabras(PEDIR_BUSQUEDA)
            buscar_tweet(palabras_buscar, tweets, tokens_ids)
            continue
        if opcion == ELIMINAR:
            palabras_eliminar = pedir_palabras(PEDIR_ELIMINACION)
            eliminar_tweet(palabras_eliminar, tweets, tokens_ids, arg)
            continue
        if opcion == IMPORTAR:
            id = importar_tweets(id, tweets, tokens_ids, arg)
            continue
        if opcion == EXPORTAR:
            exportar_tweets(tweets)
            continue
        if opcion == SALIR:
            print(FIN)
            break
        print(INPUT_INVALIDO)


# -----------------------------------------------------------------------------


def verificar_ir_atras(opcion_input):
    """
    Recibe un string o un numero, devuelve un booleano segun la comparacion
    """
    return opcion_input == ATRAS


# -----------------------------------------------------------------------------


def crear_tweet(id, tweets, tokens_ids, longitud_min, tweet_y_normalizado):
    """
    Recibe un string con la id del tweet, un diccionario de tweets,
    , un diccionario de tokens indexados y una tupla con el tweet original
    y el normalizado"

    Pide el tweet, lo normaliza y lo agrega.
    Agrega los tokens del tweet al diccionario de tokens indexados.

    Devuelve un booleano dependiendo de si se agrego o no el tweet.
    """
    if not tweet_y_normalizado:
        return False
    tweet, tweet_normalizado = tweet_y_normalizado
    agregar_tokens_indexados(id, tokens_ids, tweet_normalizado, longitud_min)
    tweets[id] = tweet
    return tweet


# -----------------------------------------------------------------------------


def pedir_tweet():
    """
    Pide un tweet hasta que se ingrese el numero 4
    o hasta que se ingrese un tweet valido.

    Devuelve el tweet ingresado y el normalizado en una tupla,
    o False si se ingreso 4.
    """
    while True:
        tweet = input("Ingrese el tweet a almacenar:\n")
        if verificar_ir_atras(tweet):
            return False
        tweet_normalizado = normalizar_texto(tweet)
        if not tweet_normalizado:
            print(INPUT_INVALIDO)
            continue
        return tweet, tweet_normalizado


# -----------------------------------------------------------------------------


def normalizar_texto(texto):
    """
    Recibe un string y lo devuelve normalizado.
    """
    texto = texto.lower()
    tweet_normalizado = ""
    letras_con_tilde = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ä": "a",
        "ë": "e",
        "ï": "i",
        "ö": "o",
        "ü": "u",
    }
    for letra in texto:
        if not (letra.isalnum() or letra == " "):
            continue
        if letra in letras_con_tilde:
            tweet_normalizado += letras_con_tilde[letra]
            continue
        tweet_normalizado += letra
    return tweet_normalizado.strip()


# -----------------------------------------------------------------------------


def tokenizar_por_segmentos(palabras, longitud_min):
    """
    Recibe una lista de strings ya normalizados.

    Los tokeniza por segmentos de 3 letras como minimo
    y los agrega a una lista, si es de menos de 3 letras
    se agrega a la lista directamente.

    Devuelve la lista de segmentos.
    """
    segmentos = []
    for palabra in palabras:
        if len(palabra) > longitud_min:
            for i in range(len(palabra)):
                longitud = i + longitud_min
                while longitud <= len(palabra):
                    if palabra[i:longitud] not in segmentos:
                        segmentos.append(palabra[i:longitud])
                    longitud += 1
        else:
            segmentos.append(palabra)
    return segmentos


# -----------------------------------------------------------------------------


def agregar_tokens_indexados(
    id_tweet, tokens_ids, tweet_normalizado, longitud_min
):
    """
    Recibe un string con la id del tweet, un diccionario de tokens indexados
    y un string normalizado.

    Tokeniza el tweet por segmentos y agrega cada segmento a la diccionario de
    tokens indexados, con su respectivo id.
    """
    palabras = tweet_normalizado.split()
    tokens = tokenizar_por_segmentos(palabras, longitud_min)
    for token in tokens:
        if token not in tokens_ids:
            tokens_ids[token] = [id_tweet]
        elif id_tweet not in tokens_ids[token]:
            tokens_ids[token].append(id_tweet)


# ---------------------------------------------------------------------------


def buscar_tweet(palabras, tweets, tokens_ids):
    """
    Recibe un string, un diccionario de tweets
    y un diccionario de tokens indexados.

    Busca las ids de los tweets que contienen esas palabras o segmentos.

    Devuelve un set con los ids encontrados o False si no se encontraron.
    """
    if not palabras:
        return False
    ids_resultantes = encontrar_tweets(palabras, tokens_ids)
    if not ids_resultantes:
        print(NO_ENCONTRADOS)
        return False
    mostrar_tweets(ids_resultantes, tweets)
    return ids_resultantes


# ---------------------------------------------------------------------------


def pedir_palabras(mensaje):
    """
    Recibe un string.

    Pide las palabras que se quieren buscar
    y las valida hasta que se ingresen correctamente o se ingrese el numero 4.

    Devuelve las palabras normalizadas y separadas en una lista
    o False si se ingresa el numero 4.
    """
    while True:
        palabras = input(mensaje)
        if verificar_ir_atras(palabras):
            return False
        palabras_normalizadas = normalizar_texto(palabras)
        if not palabras_normalizadas:
            print(INPUT_INVALIDO)
            continue
        return palabras_normalizadas.split()


# ---------------------------------------------------------------------------


def encontrar_tweets(palabras, tokens_ids):
    """
    Recibe una lista de string y un diccionario de tokens indexados.

    Verifica que cada palabra este en algun tweet.
    Busca los ids en comun.

    Devuelve el set con los ids resultantes,
    o False si la palabra no esta en ningun tweet
    o las palabras si estan pero en tweets diferentes.
    """
    ids_palabras = validar_palabras(palabras, tokens_ids)
    if not ids_palabras:
        return False
    ids_resultantes = encontrar_ids_comunes(ids_palabras)
    if not ids_resultantes:
        return False
    return ids_resultantes


# ---------------------------------------------------------------------------


def encontrar_ids_comunes(ids_palabras):
    """
    Recibe una lista de listas de ids.

    Agrega a una lista solo los ids que aparecen en todas las listas de ids
    y pasa la lista a un set para filtrar los ids repetidos.

    Devuelve el set con los ids resultantes
    o False si no hay ningun id en comun.
    """
    ids_resultantes = []
    if len(ids_palabras) == 1:
        return ids_palabras[0]
    for id in ids_palabras[0]:
        agregar = True
        for sub_id in ids_palabras[1:]:
            if id not in sub_id:
                agregar = False
                break
        if agregar:
            ids_resultantes.append(id)
    if not ids_resultantes:
        return False
    ids_resultantes = set(ids_resultantes)
    return ids_resultantes


# ---------------------------------------------------------------------------


def validar_palabras(palabras, tokens_ids):
    """
    Recibe una lista de strigs y un diccionario de tokens indexados.

    Verifica que cada palabra este en algun tweet, si estan todas,
    agrega a una lista los ids de los tweets
    en los que se encuentra cada palabra.

    Devuelve la lista con los ids
    o False si no encuentra alguna palabra
    """
    ids_palabras = []
    for palabra in palabras:
        if palabra not in tokens_ids:
            return False
        if tokens_ids[palabra] not in ids_palabras:
            ids_palabras.append(tokens_ids[palabra])
    return ids_palabras


# ---------------------------------------------------------------------------


def mostrar_tweets(ids, tweets):
    print(RESULTADOS_BUSQUEDA)
    for id in ids:
        print(f"{id}. {tweets[id]}")


# ---------------------------------------------------------------------------


def eliminar_tweet(palabras, tweets, tokens_ids, longitud_min):
    """
    Recibe un string, un diccionario de tweets y
    un diccionario de tokens indexados.

    Busca las palabras ingresadas, muestra los tweets encontrados,
    pide las ids de los tweets que se quieren eliminar, elimina los tweets
    y muestra los tweets eliminados.

    Devuelve un booleano dependiendo de si se encontro el tweet
    y si se borro o no.
    """
    tweets_encontrados = buscar_tweet(palabras, tweets, tokens_ids)
    if not tweets_encontrados:
        return False
    ids = pedir_ids(tweets)
    if not ids:
        return False
    tweets_eliminados = eliminar_tweet_e_ids_de_tokens(
        ids, tweets, tokens_ids, longitud_min
    )
    eliminar_de_db(ids)
    mostrar_tweets_eliminados(tweets_eliminados)
    return True


# ---------------------------------------------------------------------------


def pedir_ids(tweets):
    """
    Recibe un diccinario de tweets.

    Pide las ids de los tweets que se quieren eliminar
    y las valida hasta que se ingresen correctamente o se ingrese el numero 4.

    Devuelve un set con las ids normalizadas
    o False si se ingreso el numero 4.
    """
    while True:
        ids = input("Ingrese los numeros de tweets a eliminar:\n")
        if verificar_ir_atras(ids):
            return False
        ids = ids.split(",")
        ids_normalizadas = normalizar_ids(ids)
        if not ids_normalizadas:
            print(INPUT_INVALIDO)
            continue
        ids_normalizadas = set(ids_normalizadas)
        if not validar_ids(ids_normalizadas, tweets):
            print(NUMERO_INVALIDO)
            continue
        return ids_normalizadas


# ---------------------------------------------------------------------------


def normalizar_ids(ids):
    """
    Recibe un string con las id de los tweets que se quieren eliminar.

    Las normaliza y las devuelve en una lista,
    si no son validas devuelve False.
    """
    ids_normalizadas = []
    for i in range(len(ids)):
        if "-" in ids[i] and ids[i].count("-") == 1:
            rango = ids[i].split("-")
            num1 = rango[0].strip()
            num2 = rango[1].strip()
            if num1 <= num2 and num1.isnumeric() and num2.isnumeric():
                for sub_i in range(int(num1), int(num2) + 1):
                    ids_normalizadas.append(sub_i)
            else:
                return False
        elif not ids[i].strip().isnumeric():
            return False
        else:
            ids_normalizadas.append(int(ids[i]))
    return ids_normalizadas


# ---------------------------------------------------------------------------


def validar_ids(ids, tweets):
    """
    Recibe una lista con ids y un diccionario de tweets.

    Verifica que las ids existan.

    Devuelve un booleano dependiendo de si existen o no todas las ids.
    """
    for id in ids:
        if id not in tweets:
            return False
    return True


# ---------------------------------------------------------------------------


def eliminar_tweet_e_ids_de_tokens(ids, tweets, tokens_ids, longitud_min):
    """
    Recibe una lista con ids, un diccionario de tweets
    y un diccionario de token indexados.

    Agrega los tweets que va a eliminar a un diccionario
    con sus respectivos ids.
    Los elimina del diccionario de tweets
    y elimina los ids del tweet de los tokens a los que esta asociado.

    Devuelve el diccionario con los tweets eliminados.
    """
    tweets_eliminados = {}
    for id in ids:
        tweet_normalizado = normalizar_texto(tweets[id])
        palabras = tweet_normalizado.split()
        tokens = tokenizar_por_segmentos(palabras, longitud_min)
        tweets_eliminados[id] = tweets[id]

        for token in tokens:
            if len(tokens_ids[token]) > 1:
                tokens_ids[token].remove(id)
            else:
                tokens_ids.pop(token)
        tweets.pop(id)
    return tweets_eliminados


# ---------------------------------------------------------------------------


def mostrar_tweets_eliminados(tweets):
    print(TWEETS_ELIMINADOS_MENSAJE)
    for tweet in tweets:
        print(f"{tweet}. {tweets[tweet]}")


# ---------------------------------------------------------------------------


def validar_contenido_db():
    """
    Valida el contenido de los archivos del directorio db.

    Devuelve la proxima id a utilizar y una lista con los tweets validos.
    """
    tweets_validos = {}
    archivos = os.listdir(DB_PATH)
    proxima_id = len(archivos)
    if not archivos:
        return proxima_id
    for archivo in range(len(archivos)):
        with open(f"{DB_PATH}/{archivo}.txt", "r") as tweet:
            tweet = tweet.readline().strip()
            tweet_normalizado = normalizar_texto(tweet)
            if tweet_normalizado:
                tweets_validos[archivo] = (tweet, tweet_normalizado)
    return proxima_id, tweets_validos


# ---------------------------------------------------------------------------


def cargar_tweets(tweets, tokens_ids, longitud_min):
    """
    Recibe un diccionario de tweets , un diccionario de token indexados
    y la longitud minima para la tokenizacion.

    Carga los tweets en el diccionario de tweets y agrega los tokens.

    Devuelve la proxima id a utilizar.
    """
    contenido_db = validar_contenido_db()
    if not contenido_db:
        return contenido_db
    id, tweets_db = contenido_db
    for id_tweet in tweets_db:
        tweet = tweets_db[id_tweet][0]
        tweet_normalizado = tweets_db[id_tweet][1]
        crear_tweet(
            id_tweet,
            tweets,
            tokens_ids,
            longitud_min,
            (tweet, tweet_normalizado),
        )
    return id


# ---------------------------------------------------------------------------


def agregar_a_db(id, tweet):
    with open(f"{DB_PATH}/{id}.txt", "w") as archivo:
        archivo.write(tweet)


# ---------------------------------------------------------------------------


def eliminar_de_db(ids):
    for id in ids:
        with open(f"{DB_PATH}/{id}.txt", "w") as archivo:
            archivo.write("")


# ---------------------------------------------------------------------------


def pedir_rutas():
    """
    Pide una ruta hasta que se ingrese **
    o hasta que se ingrese una ruta valida.

    Devuelve los archivos validos de esa ruta.
    """
    while True:
        rutas = input("Ingrese la ruta del archivo a cargar:")
        if verificar_ir_atras(rutas):
            return False
        if rutas.strip() == "":
            print(ERROR_IMPORTACION)
            continue
        archivos = validar_paths(rutas.split())
        if archivos == []:
            print("OK 0")
            return False
        if not archivos:
            print(ERROR_IMPORTACION)
            continue
        archivos_validos = validar_contenido(archivos)
        if archivos_validos == []:
            print("OK 0")
            return False
        return archivos_validos


# ---------------------------------------------------------------------------


def validar_paths(rutas, directorio_actual=""):
    """
    Recibe una lista de rutas y el directorio actual.

    Devuelve una lista con las rutas validas.
    """
    rutas_validas = []
    for ruta in rutas:
        ruta = os.path.join(directorio_actual, ruta)
        if not os.path.exists(ruta):
            return False
        if os.path.isdir(ruta):
            rutas_validas += validar_paths(os.listdir(ruta), ruta)
        elif ruta.lower().endswith(".txt"):
            rutas_validas.append(ruta)
        elif directorio_actual == "":
            return False
    return rutas_validas


# ---------------------------------------------------------------------------


def validar_contenido(archivos):
    """
    Recibe una lista de archivos txt.

    Devuelve una lista con las lineas validas de cada archivo.
    """
    contenido_valido = []
    for archivo in archivos:
        with open(archivo, "r") as tweets:
            for tweet in tweets:
                tweet = tweet.strip()
                tweet_normalizado = normalizar_texto(tweet)
                if tweet_normalizado:
                    contenido_valido.append((tweet, tweet_normalizado))
    return contenido_valido


# ---------------------------------------------------------------------------


def importar_tweets(id, tweets, tokens_ids, longitud_min):
    """
    Recibe el proximo id a utilizar, un diccionario de tweets, un diccionario
    de tokens indexados y el numero minimo de tokenizacion.

    Pide las rutas y agrega los tweets de los archivos validos.

    Devuelve el proximo id a utilizar.
    """
    tweets_importados = pedir_rutas()
    cant_tweets = 0
    if not tweets_importados:
        return id
    for tweet_importado in tweets_importados:
        nuevo_tweet = crear_tweet(
            id, tweets, tokens_ids, longitud_min, tweet_importado
        )
        agregar_a_db(id, nuevo_tweet)
        cant_tweets += 1
        id += 1
    print(f"OK {cant_tweets}")
    return id


# ---------------------------------------------------------------------------


def pedir_ruta_exportacion():
    """
    Pide una ruta hasta que se ingrese **
    o hasta que se ingrese una ruta valida.

    Devuelve la ruta si la misma es valida, o False si se ingresa **.
    """
    while True:
        ruta = input("Ingrese la ruta del archivo a guardar:")
        if verificar_ir_atras(ruta):
            return False
        ruta_separada = ruta.split("/")
        subdirectorios = "/".join(ruta_separada[:-1]).strip()
        archivo = ruta_separada[-1]
        if not subdirectorios and archivo.lower().endswith(".txt"):
            return ruta
        if os.path.exists(subdirectorios) and archivo.lower().endswith(".txt"):
            return ruta
        print(DIRECCION_ERRONEA)


# ---------------------------------------------------------------------------


def exportar_tweets(tweets):
    """
    Recibe un diccionario de tweets.

    Exporta todos los tweets que hay en memoria a la ruta especificada.
    """
    ruta = pedir_ruta_exportacion()
    if not ruta:
        return
    with open(ruta, "w") as archivo:
        cant_tweets = 0
        for id in tweets:
            archivo.write(f"{tweets[id]}\n")
            cant_tweets += 1
    print(f"OK {cant_tweets}")
    return


# ---------------------------------------------------------------------------


def validar_args(args):
    """
    Recibe una lista con los argumentos que recible el programa.

    Devuelve el numero minimo para la tokenizacion o False si el argumento
    es invalido.
    """
    args = args[1:]
    if not args:
        return DEFAULT_PARAM
    if len(args) == 1 and args[0].isnumeric() and int(args[0]) > 0:
        return int(args[0])
    return False


# ---------------------------------------------------------------------------
# Esta parte del código se ejecuta al final,
# asegurando que se ejecute el programa
# mediante la terminal correctamente y permitiendo que se puedan realizar
# los tests de forma automática y aislada.
if __name__ == "__main__":
    args = sys.argv
    main(args)
