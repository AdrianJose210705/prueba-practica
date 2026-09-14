import pygame
import random
import sys
from inicio import boton

pygame.init()

# Configuración de ventana
ANCHO, ALTO = 800, 600

# CREAR VENTANA
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Encuentra al Intruso")

# Define el reloj
clock = pygame.time.Clock()

# Colores
BLANCO = (245, 245, 245)
NEGRO = (30, 30, 30)
VERDE = (46, 204, 113)
ROJO = (231, 76, 60)

# Datos de elementos (Normal vs Intruso)
CATEGORIAS = [
    {"normal": "🐱", "intruso": "🐶"},
    {"normal": "🍎", "intruso": "🍅"},
    {"normal": "⚽", "intruso": "🏀"},
    {"normal": "🚗", "intruso": "🏎️"},
    {"normal": "7", "intruso": "6"},
]

# Estado del juego
puntuacion = 0
penalizacion = 0
penalizacion_tiempo = 0
posiciones_intrusos = set()
tiempo_restante = 60.0
tiempo_inicial_frame = 0
estado_juego = "MENU" #CONTROLA SI ESTAMOS EN EL MENU O JUGANDO

fuente = pygame.font.SysFont("Segoe UI Emoji", 40)
fuente_texto = pygame.font.SysFont("Arial", 24, bold=True)
fuente_titulo = pygame.font.SysFont("Arial", 48, bold=True)

# IMAGEN DE FONDO DE PANTALLA
background = pygame.image.load("fondo.jpg").convert()
# AJUSTE DE LA IMAGEN PARA ADAPTACION A LA PANTALLA
background = pygame.transform.scale(background, (ANCHO, ALTO))

#Texto que se encuentra dentro del boton
boton_inicio = boton(pantalla, "Jugar")
boton_facil = boton(pantalla, "Facil")
boton_regresar = boton(pantalla, "Regresar")
boton_medio = boton(pantalla, "Medio")
boton_dificil = boton(pantalla, "Dificil")
boton_extremo = boton(pantalla, "Extremo")
boton_salir = boton(pantalla, "Salir")

# Mueve el boton y aplica un margen de 20px
boton_regresar.rect.topleft = (20, 20)
boton_medio.rect.centerx = (ANCHO // 2)
boton_facil.rect.centerx = (ANCHO // 2) - 220
boton_dificil.rect.centerx = (ANCHO // 2) + 220
boton_extremo.rect.centery = (ALTO // 1.5)
boton_salir.rect.topright = (ANCHO - 20, 20)

# Recalcula la posicion del texto dentro del boton 
boton_regresar.prepara_texto("Regresar")
boton_medio.prepara_texto("Medio")
boton_facil.prepara_texto("Facil")
boton_dificil.prepara_texto("Dificil")
boton_extremo.prepara_texto("Extremo")
boton_salir.prepara_texto("Salir")

# Variable para guardar la dificultad seleccionada ("FACIL", "MEDIO", "DIFICIL", "EXTREMO")
dificultad_actual = "FACIL"

def generar_nivel(dificultad):
    # Configuración según la dificultad seleccionada y cantidad de intrusos
    if dificultad == "FACIL":
        filas, columnas = 2, 2
        cant_intrusos = 1
    elif dificultad == "MEDIO":
        filas, columnas = 4, 4
        cant_intrusos = 1
    elif dificultad == "DIFICIL":
        filas, columnas = 6, 6
        cant_intrusos = 1
    elif dificultad == "EXTREMO":
        filas, columnas = 8, 8
        cant_intrusos = 1

    cat = random.choice(CATEGORIAS)
    
    # Generar la matriz llena con el elemento normal
    grid = [[cat["normal"] for _ in range(columnas)] for _ in range(filas)]

    # Colocar las posiciones de los intrusos de forma aleatoria sin repetir
    posiciones_intrusos = set()
    while len(posiciones_intrusos) < cant_intrusos:
        pos_x = random.randint(0, columnas - 1)
        pos_y = random.randint(0, filas - 1)
        posiciones_intrusos.add((pos_x, pos_y))

    for pos_x, pos_y in posiciones_intrusos:
        grid[pos_y][pos_x] = cat["intruso"]

    return grid, posiciones_intrusos

# Bucle principal
while True:
    # IMAGEN DE FONDO QUE CUBRE TODA LA PANTALLA 
    pantalla.blit(background, [0, 0])
    clic = False

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if evento.type == pygame.MOUSEBUTTONDOWN:
            clic = True

    mouse_pos = pygame.mouse.get_pos()

    if estado_juego == "MENU":
        # Título del menú
        titulo = fuente_titulo.render("Encuentra al Intruso", True, BLANCO)
        pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 150))
        
        # Dibujar botón de inicio
        boton_inicio.dibuja_boton()
        
        # Iniciar juego al hacer clic en el botón
        if clic and boton_inicio.rect.collidepoint(mouse_pos):
            estado_juego = "DIFICULTAD"

    elif estado_juego == "DIFICULTAD":
        # Titulo de la dificultad
        titulo = fuente_titulo.render("Dificultad", True, BLANCO)
        pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 150))
        
        # Dibujar botón 
        boton_facil.dibuja_boton()
        boton_regresar.dibuja_boton()
        boton_medio.dibuja_boton()
        boton_dificil.dibuja_boton()
        boton_extremo.dibuja_boton()
        
        # Iniciar juego al hacer clic en cualquiera de las dificultades
        if clic:
            if boton_facil.rect.collidepoint(mouse_pos):
                dificultad_actual = "FACIL"
                grid, posiciones_intrusos = generar_nivel(dificultad_actual)
                tiempo_restante = 60.0
                estado_juego = "JUGANDO"
            elif boton_medio.rect.collidepoint(mouse_pos):
                dificultad_actual = "MEDIO"
                grid, posiciones_intrusos = generar_nivel(dificultad_actual)
                tiempo_restante = 60.0
                estado_juego = "JUGANDO"
            elif boton_dificil.rect.collidepoint(mouse_pos):
                dificultad_actual = "DIFICIL"
                grid, posiciones_intrusos = generar_nivel(dificultad_actual)
                tiempo_restante = 60.0
                estado_juego = "JUGANDO"
            elif boton_extremo.rect.collidepoint(mouse_pos):
                dificultad_actual = "EXTREMO"
                grid, posiciones_intrusos = generar_nivel(dificultad_actual)
                tiempo_restante = 60.0
                estado_juego = "JUGANDO"
            # Regresa al menu principal
            elif boton_regresar.rect.collidepoint(mouse_pos):
                estado_juego = "MENU"

    elif estado_juego == "JUGANDO":
        # Dibuja el boton
        boton_salir.dibuja_boton()
        
        # Regresa a dificuldad al hacer clik en salir
        if clic and boton_salir.rect.collidepoint(mouse_pos):
            puntuacion = 0
            estado_juego = "DIFICULTAD"
        
        # Logica del temporizador
        if dificultad_actual in ["FACIL","MEDIO", "DIFICIL", "EXTREMO"]:
            # Descuenta el tiempo por cada fotograma (30 FPS)
            tiempo_restante -= 1 / 30.0
            
            # Dibuja el temporizador en la esquina superior izquierda
            txt_tiempo = fuente_texto.render(f"Tiempo: {max(0, int(tiempo_restante))}s", True, BLANCO)
            pantalla.blit(txt_tiempo, (20, 50))

            # Si el tiempo llega a 0 termina la partida
            if tiempo_restante <= 0:
                estado_juego = "GAME_OVER"
        
        txt_info = fuente_texto.render(f"Puntos: {puntuacion}", True, BLANCO)
        pantalla.blit(txt_info, (20, 20))

        # Obtener filas y columnas dinámicamente desde la matriz grid
        filas = len(grid)
        columnas = len(grid[0])

        margen_x, margen_y = 100, 100
        ancho_celda = (ANCHO - 2 * margen_x) // columnas
        alto_celda = (ALTO - 2 * margen_y) // filas

        for r in range(filas):
            for c in range(columnas):
                x = margen_x + c * ancho_celda
                y = margen_y + r * alto_celda
                rect = pygame.Rect(x, y, ancho_celda - 5, alto_celda - 5)

                pygame.draw.rect(pantalla, (220, 220, 220), rect, border_radius=8)

                texto = fuente.render(grid[r][c], True, NEGRO)
                pantalla.blit(texto, (x + (ancho_celda - texto.get_width()) // 2, y + (alto_celda - texto.get_height()) // 2))

                # Detección de clic en la celda
                if clic and rect.collidepoint(mouse_pos):
                    if (c, r) in posiciones_intrusos:
                        puntuacion += 10
                        # Bonificación de tiempo según la dificultad
                        if dificultad_actual in ["MEDIO", "FACIL"]:
                            tiempo_restante += 1.5
                        elif dificultad_actual in ["DIFICIL", "EXTREMO"]:
                            tiempo_restante += 1.0
                        grid, posiciones_intrusos = generar_nivel(dificultad_actual)
                    else:
                        # Penalización según la dificultad activa
                        if dificultad_actual == "FACIL":
                            penalizacion = 5
                            penalizacion_tiempo = 0.2
                        elif dificultad_actual == "MEDIO":
                            penalizacion = 10
                            penalizacion_tiempo = 0.4
                        elif dificultad_actual == "DIFICIL":
                            penalizacion = 10
                            penalizacion_tiempo = 0.5
                        elif dificultad_actual == "EXTREMO":
                            penalizacion = 15
                            penalizacion_tiempo = 0.5
                        
                        tiempo_restante -= penalizacion_tiempo
                        puntuacion = max(0, puntuacion - penalizacion)
    
    elif estado_juego == "GAME_OVER":
        # Muestra un mensaje de que ya termino todo
        txt_fin = fuente_titulo.render("¡TIEMPO AGOTADO!", True, ROJO)
        txt_puntos = fuente_texto.render(f"Puntuación Final: {puntuacion}", True, BLANCO)
        
        pantalla.blit(txt_fin, (ANCHO // 2 - txt_fin.get_width() // 2, ALTO // 2 - 50))
        pantalla.blit(txt_puntos, (ANCHO // 2 - txt_puntos.get_width() // 2, ALTO // 2 + 10))
        
        boton_regresar.dibuja_boton()
        if clic and boton_regresar.rect.collidepoint(mouse_pos):
            puntuacion = 0
            estado_juego = "DIFICULTAD"
                    
    pygame.display.flip()
    clock.tick(30)