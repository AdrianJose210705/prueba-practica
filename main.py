import json
import os
import random
import sys
import pygame
from inicio import boton


class JuegoIntruso:

  def __init__(self):
    # Inicialización de módulos principales de Pygame
    pygame.init()
    pygame.mixer.init()

    # --- CONFIGURACIÓN DE VENTANA ---
    self.ANCHO, self.ALTO = 1280, 720
    self.pantalla = pygame.display.set_mode((self.ANCHO, self.ALTO))
    pygame.display.set_caption("Encuentra al Intruso")

    # Control de tasa de refresco (FPS)
    self.clock = pygame.time.Clock()

    # --- PALETA DE COLORES ---
    self.BLANCO = (245, 245, 245)
    self.NEGRO = (30, 30, 30)
    self.VERDE = (46, 204, 113)  # Usado para acierto en la casilla
    self.ROJO = (231, 76, 60)  # Usado para fallo en la casilla
    self.AMARILLO = (255, 255, 0)
    self.GRIS_CELDA = (220, 220, 220)

    # --- BASE DE DATOS DE CATEGORÍAS Y ELEMENTOS ---
    self.CATEGORIAS = {
        "FRUTAS": [
            {"normal": "🍎", "intruso": "🍐"},
            {"normal": "🍌", "intruso": "🍋"},
            {"normal": "🍓", "intruso": "🍒"},
            {"normal": "🍊", "intruso": "🍑"},
        ],
        "FUTBOL": [
            {"normal": "⚽", "intruso": "🏀"},
            {"normal": "🏆", "intruso": "🥇"},
            {"normal": "🎽", "intruso": "👕"},
            {"normal": "👟", "intruso": "🥾"},
        ],
        "EMOJIS": [
            {"normal": "😀", "intruso": "😁"},
            {"normal": "😎", "intruso": "🤓"},
            {"normal": "😡", "intruso": "🤬"},
            {"normal": "😴", "intruso": "😪"},
        ],
    }

    # --- CONFIGURACIÓN Y ESTADO INICIAL ---
    self.categoria_seleccionada = "FRUTAS"
    self.dificultad_actual = "FACIL"
    self.pareja_actual = None

    self.puntuacion = 0
    self.vidas = 3  # Sistema de 3 vidas
    self.estado_juego = "MENU"
    self.estado_anterior = "MENU"
    self.grid = []
    self.posiciones_intrusos = set()

    # --- FEEDBACK VISUAL SIN BLOQUEAR PANTALLA ---
    self.casilla_feedback = None
    self.tiempo_feedback = 0

    # --- SISTEMA DE PUNTAJES MÁXIMOS (PERSISTENCIA) ---
    self.archivo_scores = "scores.json"
    self.scores = self.cargar_scores()

    # --- CARGA ÚNICA DE EFECTOS SONOROS Y MÚSICA ---
    try:
      self.snd_correcto = pygame.mixer.Sound("correcto.mp3")
      self.snd_incorrecto = pygame.mixer.Sound("incorrecto.mp3")
      self.snd_click = pygame.mixer.Sound("click.mp3")

      self.snd_correcto.set_volume(0.7)
      self.snd_incorrecto.set_volume(0.3)
      self.snd_click.set_volume(0.5)

      # Cargar y reproducir música de fondo en bucle infinito (-1)
      pygame.mixer.music.load("musica_fondo2.mp3")
      pygame.mixer.music.set_volume(0.3)
      pygame.mixer.music.play(-1)

    except Exception as e:
      print(f"Aviso: No se pudieron cargar los recursos de audio: {e}")
      self.snd_correcto = None
      self.snd_incorrecto = None
      self.snd_click = None

    # --- FUENTES Y TIPOGRAFÍAS ---
    self.fuente_emoji = pygame.font.SysFont("Segoe UI Emoji", 26)
    self.fuente = pygame.font.SysFont("Segoe UI Emoji", 40)
    self.fuente_texto = pygame.font.SysFont("Arial", 24, bold=True)
    self.fuente_titulo = pygame.font.SysFont("Arial", 48, bold=True)

    # --- RECURSOS GRÁFICOS (FONDO) ---
    self.background = pygame.image.load("imagan_inicio1.png").convert()
    self.background = pygame.transform.scale(
        self.background, (self.ANCHO, self.ALTO)
    )

    # Inicialización de la interfaz de botones
    self.inicializar_botones()

  def reproducir_click(self):
    """Auxiliar para reproducir el sonido de clic de botón."""
    if self.snd_click:
      self.snd_click.play()

  def cargar_scores(self):
    """Carga los puntajes máximos desde el archivo JSON si existe."""
    scores_predeterminados = {
        "FACIL": 0,
        "MEDIO": 0,
        "DIFICIL": 0,
        "EXTREMO": 0,
    }
    if os.path.exists(self.archivo_scores):
      try:
        with open(self.archivo_scores, "r") as f:
          datos = json.load(f)
          for dif in scores_predeterminados:
            if dif in datos:
              if isinstance(datos[dif], dict):
                scores_predeterminados[dif] = datos[dif].get("maximo", 0)
              elif isinstance(datos[dif], int):
                scores_predeterminados[dif] = datos[dif]
      except Exception:
        pass

    return scores_predeterminados

  def guardar_scores(self):
    """Guarda las puntuaciones actuales en el archivo JSON."""
    try:
      with open(self.archivo_scores, "w") as f:
        json.dump(self.scores, f, indent=4)
    except Exception as e:
      print(f"Error al guardar scores: {e}")

  def registrar_puntuacion(self, dificultad, puntos):
    """Actualiza la puntuación máxima registrada si se supera el récord."""
    if puntos > self.scores.get(dificultad, 0):
      self.scores[dificultad] = puntos
      self.guardar_scores()

  def inicializar_botones(self):
    """Crea y posiciona todos los botones con una distribución limpia."""
    self.boton_inicio = boton(self.pantalla, "Jugar")
    self.boton_score = boton(self.pantalla, "Score")
    self.boton_facil = boton(self.pantalla, "Facil")
    self.boton_medio = boton(self.pantalla, "Medio")
    self.boton_dificil = boton(self.pantalla, "Dificil")
    self.boton_extremo = boton(self.pantalla, "Extremo")
    self.boton_regresar = boton(self.pantalla, "Regresar")
    self.boton_salir = boton(self.pantalla, "Salir")
    self.boton_frutas = boton(self.pantalla, "Frutas")
    self.boton_futbol = boton(self.pantalla, "Futbol")
    self.boton_emojis = boton(self.pantalla, "Emojis")

    # Botones de la pantalla de Juego Terminado
    self.boton_reiniciar = boton(self.pantalla, "Reiniciar")
    self.boton_score_go = boton(self.pantalla, "Score")
    self.boton_salir1 = boton(self.pantalla, "Salir")

    # --- MENÚ PRINCIPAL ---
    self.boton_inicio.rect.center = (self.ANCHO // 2, self.ALTO // 2 - 20)
    self.boton_score.rect.center = (self.ANCHO // 2, self.ALTO // 2 + 70)

    # --- BOTONES GENERALES DE NAVEGACIÓN ---
    self.boton_regresar.rect.topleft = (30, 30)
    self.boton_salir.rect.topright = (self.ANCHO - 30, 30)

    # --- PANTALLA DE DIFICULTAD (Distribución 2x2 centrada) ---
    self.boton_facil.rect.center = (
        self.ANCHO // 2 - 140,
        self.ALTO // 2 - 10,
    )
    self.boton_medio.rect.center = (
        self.ANCHO // 2 + 140,
        self.ALTO // 2 - 10,
    )
    self.boton_dificil.rect.center = (
        self.ANCHO // 2 - 140,
        self.ALTO // 2 + 80,
    )
    self.boton_extremo.rect.center = (
        self.ANCHO // 2 + 140,
        self.ALTO // 2 + 80,
    )

    # --- PANTALLA DE CATEGORÍA (Disposición en fila centrada) ---
    self.boton_frutas.rect.center = (
        self.ANCHO // 2 - 260,
        self.ALTO // 2 + 40,
    )
    self.boton_emojis.rect.center = (self.ANCHO // 2, self.ALTO // 2 + 40)
    self.boton_futbol.rect.center = (
        self.ANCHO // 2 + 260,
        self.ALTO // 2 + 40,
    )

    # --- GAME OVER ---
    self.boton_reiniciar.rect.center = (self.ANCHO // 2, self.ALTO // 2 + 20)
    self.boton_score_go.rect.center = (self.ANCHO // 2, self.ALTO // 2 + 95)
    self.boton_salir1.rect.center = (self.ANCHO // 2, self.ALTO // 2 + 170)

    # Renderizado inicial del texto en cada botón
    for b, txt in [
        (self.boton_inicio, "Jugar"),
        (self.boton_score, "Score"),
        (self.boton_regresar, "Regresar"),
        (self.boton_medio, "Medio"),
        (self.boton_facil, "Facil"),
        (self.boton_dificil, "Dificil"),
        (self.boton_extremo, "Extremo"),
        (self.boton_salir, "Salir"),
        (self.boton_frutas, "Frutas"),
        (self.boton_futbol, "Futbol"),
        (self.boton_emojis, "Emojis"),
        (self.boton_reiniciar, "Reiniciar"),
        (self.boton_score_go, "Score"),
        (self.boton_salir1, "Salir"),
    ]:
      b.prepara_texto(txt)

  def generar_nivel(self, dificultad, categoria):
    """Genera una nueva ronda de juego seleccionando dimensiones e íconos."""
    if dificultad == "FACIL":
      filas, columnas = 2, 2
    elif dificultad == "MEDIO":
      filas, columnas = 4, 4
    elif dificultad == "DIFICIL":
      filas, columnas = 6, 6
    elif dificultad == "EXTREMO":
      filas, columnas = 8, 8

    self.pareja_actual = random.choice(self.CATEGORIAS[categoria])
    return self.reubicar_intruso(filas, columnas, self.pareja_actual)

  def reubicar_intruso(self, filas, columnas, pareja):
    """Crea la cuadrícula y reubica el ícono intruso en una coordenada aleatoria."""
    grid = [[pareja["normal"] for _ in range(columnas)] for _ in range(filas)]

    pos_x = random.randint(0, columnas - 1)
    pos_y = random.randint(0, filas - 1)

    posiciones_intrusos = {(pos_x, pos_y)}
    grid[pos_y][pos_x] = pareja["intruso"]

    return grid, posiciones_intrusos

  def aplicar_penalizacion(self):
    """Resta 1 vida y deduce puntos según la dificultad tras un fallo."""
    penalizaciones = {
        "FACIL": 5,
        "MEDIO": 5,
        "DIFICIL": 10,
        "EXTREMO": 15,
    }
    pts_penal = penalizaciones.get(self.dificultad_actual, 5)
    self.vidas -= 1  # Resta 1 vida por error
    self.puntuacion = max(0, self.puntuacion - pts_penal)

  def ejecutar(self):
    """Bucle principal de ejecución y renderizado del juego."""
    ejecutando = True

    while ejecutando:
      dt = self.clock.tick(60) / 1000.0
      tiempo_actual = pygame.time.get_ticks()
      self.pantalla.blit(self.background, [0, 0])
      clic = False

      # --- MANEJO DE EVENTOS TECLADO/MOUSE ---
      for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
          ejecutando = False
        elif evento.type == pygame.MOUSEBUTTONDOWN:
          if evento.button == 1:
            clic = True
        elif evento.type == pygame.KEYDOWN:
          if evento.key == pygame.K_ESCAPE:
            self.reproducir_click()
            if self.estado_juego in ["DIFICULTAD", "CATEGORIA"]:
              self.estado_juego = "MENU"
            elif self.estado_juego == "SCORES":
              self.estado_juego = self.estado_anterior
            elif self.estado_juego == "JUGANDO":
              self.registrar_puntuacion(
                  self.dificultad_actual, self.puntuacion
              )
              self.estado_juego = "GAME_OVER"
            elif self.estado_juego in ["MENU", "GAME_OVER"]:
              ejecutando = False

      mouse_pos = pygame.mouse.get_pos()

      # --- ESTADO: MENU PRINCIPAL ---
      if self.estado_juego == "MENU":
        titulo = self.fuente_titulo.render(
            "Encuentra al Intruso", True, self.NEGRO
        )
        self.pantalla.blit(
            titulo, (self.ANCHO // 2 - titulo.get_width() // 2, 150)
        )

        self.boton_inicio.dibuja_boton()
        self.boton_score.dibuja_boton()

        if clic:
          if self.boton_inicio.rect.collidepoint(mouse_pos):
            self.reproducir_click()
            self.estado_juego = "DIFICULTAD"
          elif self.boton_score.rect.collidepoint(mouse_pos):
            self.reproducir_click()
            self.estado_anterior = "MENU"
            self.estado_juego = "SCORES"

      # --- ESTADO: TABLA DE PUNTAJES (SCORES) ---
      elif self.estado_juego == "SCORES":
        titulo = self.fuente_titulo.render(
            "Puntuaciones Máximas", True, self.NEGRO
        )
        self.pantalla.blit(
            titulo, (self.ANCHO // 2 - titulo.get_width() // 2, 120)
        )

        self.boton_regresar.dibuja_boton()

        y_offset = 220
        encabezado = self.fuente_texto.render(
            f"{'DIFICULTAD':<20} {'PUNTAJE MÁXIMO':<15}", True, self.NEGRO
        )
        self.pantalla.blit(
            encabezado, (self.ANCHO // 2 - encabezado.get_width() // 2, y_offset)
        )

        y_offset += 50
        for dif in ["FACIL", "MEDIO", "DIFICIL", "EXTREMO"]:
          max_score = self.scores.get(dif, 0)
          linea_txt = f"{dif:<20} {max_score:<15}"
          txt_rendered = self.fuente_texto.render(linea_txt, True, self.NEGRO)
          self.pantalla.blit(
              txt_rendered,
              (self.ANCHO // 2 - txt_rendered.get_width() // 2, y_offset),
          )
          y_offset += 45

        if clic and self.boton_regresar.rect.collidepoint(mouse_pos):
          self.reproducir_click()
          self.estado_juego = self.estado_anterior

      # --- ESTADO: SELECCIÓN DE DIFICULTAD ---
      elif self.estado_juego == "DIFICULTAD":
        titulo = self.fuente_titulo.render("Dificultad", True, self.NEGRO)
        self.pantalla.blit(
            titulo, (self.ANCHO // 2 - titulo.get_width() // 2, 150)
        )

        self.boton_facil.dibuja_boton()
        self.boton_medio.dibuja_boton()
        self.boton_dificil.dibuja_boton()
        self.boton_extremo.dibuja_boton()
        self.boton_regresar.dibuja_boton()

        if clic:
          if self.boton_facil.rect.collidepoint(mouse_pos):
            self.reproducir_click()
            self.dificultad_actual = "FACIL"
            self.estado_juego = "CATEGORIA"
          elif self.boton_medio.rect.collidepoint(mouse_pos):
            self.reproducir_click()
            self.dificultad_actual = "MEDIO"
            self.estado_juego = "CATEGORIA"
          elif self.boton_dificil.rect.collidepoint(mouse_pos):
            self.reproducir_click()
            self.dificultad_actual = "DIFICIL"
            self.estado_juego = "CATEGORIA"
          elif self.boton_extremo.rect.collidepoint(mouse_pos):
            self.reproducir_click()
            self.dificultad_actual = "EXTREMO"
            self.estado_juego = "CATEGORIA"
          elif self.boton_regresar.rect.collidepoint(mouse_pos):
            self.reproducir_click()
            self.estado_juego = "MENU"

      # --- ESTADO: SELECCIÓN DE CATEGORÍA ---
      elif self.estado_juego == "CATEGORIA":
        titulo = self.fuente_titulo.render(
            "Selecciona Categoría", True, self.NEGRO
        )
        self.pantalla.blit(
            titulo, (self.ANCHO // 2 - titulo.get_width() // 2, 120)
        )

        self.boton_frutas.dibuja_boton()
        self.boton_futbol.dibuja_boton()
        self.boton_emojis.dibuja_boton()
        self.boton_regresar.dibuja_boton()

        if clic:
          categoria_elegida = None
          if self.boton_frutas.rect.collidepoint(mouse_pos):
            self.reproducir_click()
            categoria_elegida = "FRUTAS"
          elif self.boton_futbol.rect.collidepoint(mouse_pos):
            self.reproducir_click()
            categoria_elegida = "FUTBOL"
          elif self.boton_emojis.rect.collidepoint(mouse_pos):
            self.reproducir_click()
            categoria_elegida = "EMOJIS"
          elif self.boton_regresar.rect.collidepoint(mouse_pos):
            self.reproducir_click()
            self.estado_juego = "DIFICULTAD"

          if categoria_elegida:
            self.categoria_seleccionada = categoria_elegida
            self.puntuacion = 0
            self.vidas = 3
            self.grid, self.posiciones_intrusos = self.generar_nivel(
                self.dificultad_actual, self.categoria_seleccionada
            )
            self.casilla_feedback = None
            self.estado_juego = "JUGANDO"

      # --- ESTADO: LÓGICA DE JUEGO PRINCIPAL ---
      elif self.estado_juego == "JUGANDO":
        self.boton_salir.dibuja_boton()

        if clic and self.boton_salir.rect.collidepoint(mouse_pos):
          self.reproducir_click()
          self.registrar_puntuacion(self.dificultad_actual, self.puntuacion)
          self.estado_juego = "GAME_OVER"

        # DIBUJAR PUNTUACIÓN Y CORAZONES DE VIDAS
        txt_info = self.fuente_texto.render(
            f"Puntos: {self.puntuacion}", True, self.NEGRO
        )
        self.pantalla.blit(txt_info, (20, 20))

        string_corazones = "❤️ " * self.vidas
        txt_vidas = self.fuente_emoji.render(
            f"Vidas: {string_corazones}", True, self.NEGRO
        )
        self.pantalla.blit(txt_vidas, (20, 55))

        filas = len(self.grid)
        columnas = len(self.grid[0])

        margen_x, margen_y = 100, 100
        ancho_celda = (self.ANCHO - 2 * margen_x) // columnas
        alto_celda = (self.ALTO - 2 * margen_y) // filas

        if self.casilla_feedback and tiempo_actual >= self.tiempo_feedback:
          pos_fb, es_correcto = self.casilla_feedback
          self.casilla_feedback = None

          if es_correcto:
            self.puntuacion += 25
            self.grid, self.posiciones_intrusos = self.generar_nivel(
                self.dificultad_actual, self.categoria_seleccionada
            )
          else:
            self.aplicar_penalizacion()

            if self.vidas <= 0:
              self.registrar_puntuacion(
                  self.dificultad_actual, self.puntuacion
              )
              self.estado_juego = "GAME_OVER"
            else:
              self.grid, self.posiciones_intrusos = self.reubicar_intruso(
                  filas, columnas, self.pareja_actual
              )

        # DIBUJADO DE MATRIZ Y COMPROBACIÓN DE CLIC EN CELDAS
        for r in range(filas):
          for c in range(columnas):
            x = margen_x + c * ancho_celda
            y = margen_y + r * alto_celda
            rect = pygame.Rect(x, y, ancho_celda - 5, alto_celda - 5)

            color_celda = self.GRIS_CELDA

            if self.casilla_feedback and self.casilla_feedback[0] == (c, r):
              color_celda = (
                  self.VERDE if self.casilla_feedback[1] else self.ROJO
              )

            pygame.draw.rect(self.pantalla, color_celda, rect, border_radius=8)
            texto = self.fuente.render(self.grid[r][c], True, self.NEGRO)
            self.pantalla.blit(
                texto,
                (
                    x + (ancho_celda - texto.get_width()) // 2,
                    y + (alto_celda - texto.get_height()) // 2,
                ),
            )

            if (
                clic
                and rect.collidepoint(mouse_pos)
                and not self.casilla_feedback
            ):
              es_intruso = (c, r) in self.posiciones_intrusos

              if es_intruso:
                if self.snd_correcto:
                  self.snd_correcto.play()
              else:
                if self.snd_incorrecto:
                  self.snd_incorrecto.play()

              self.casilla_feedback = ((c, r), es_intruso)
              self.tiempo_feedback = tiempo_actual + 300

      # --- ESTADO: GAME OVER (FIN DEL JUEGO) ---
      elif self.estado_juego == "GAME_OVER":
        txt_fin = self.fuente_titulo.render("JUEGO TERMINADO", True, self.ROJO)
        txt_mensaje = self.fuente_texto.render(
            "Te has quedado sin vidas deseas reiniciar", True, self.NEGRO
        )
        txt_puntos = self.fuente_texto.render(
            f"Puntuación Final: {self.puntuacion}", True, self.NEGRO
        )

        self.pantalla.blit(
            txt_fin,
            (self.ANCHO // 2 - txt_fin.get_width() // 2, self.ALTO // 2 - 170),
        )
        self.pantalla.blit(
            txt_mensaje,
            (
                self.ANCHO // 2 - txt_mensaje.get_width() // 2,
                self.ALTO // 2 - 110,
            ),
        )
        self.pantalla.blit(
            txt_puntos,
            (
                self.ANCHO // 2 - txt_puntos.get_width() // 2,
                self.ALTO // 2 - 60,
            ),
        )

        self.boton_reiniciar.dibuja_boton()
        self.boton_score_go.dibuja_boton()
        self.boton_salir1.dibuja_boton()

        if clic:
          if self.boton_reiniciar.rect.collidepoint(mouse_pos):
            self.reproducir_click()
            self.puntuacion = 0
            self.vidas = 3
            self.grid, self.posiciones_intrusos = self.generar_nivel(
                self.dificultad_actual, self.categoria_seleccionada
            )
            self.casilla_feedback = None
            self.estado_juego = "JUGANDO"
          elif self.boton_score_go.rect.collidepoint(mouse_pos):
            self.reproducir_click()
            self.estado_anterior = "GAME_OVER"
            self.estado_juego = "SCORES"
          elif self.boton_salir1.rect.collidepoint(mouse_pos):
            self.reproducir_click()
            self.puntuacion = 0
            self.estado_juego = "MENU"

      pygame.display.flip()

    pygame.quit()


def main():
  juego = JuegoIntruso()
  juego.ejecutar()


if __name__ == "__main__":
  main()