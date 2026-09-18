import json
import os
import random
import sys
import pygame
from inicio import boton


class JuegoIntruso:

  def __init__(self):
    pygame.init()

    # Configuración de ventana estandarizada
    self.ANCHO, self.ALTO = 1280, 720
    self.pantalla = pygame.display.set_mode((self.ANCHO, self.ALTO))
    pygame.display.set_caption("Encuentra al Intruso")

    self.clock = pygame.time.Clock()

    # Colores
    self.BLANCO = (245, 245, 245)
    self.NEGRO = (30, 30, 30)
    self.VERDE = (46, 204, 113)
    self.ROJO = (231, 76, 60)
    self.AMARILLO = (255, 255, 0)

    # Base de datos de categorías
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

    self.categoria_seleccionada = "FRUTAS"
    self.dificultad_actual = "FACIL"

    # Estado del juego
    self.puntuacion = 0
    self.tiempo_restante = 60.0
    self.estado_juego = "MENU"
    self.estado_anterior = "MENU"  # Guarda el estado previo a ver los scores
    self.grid = []
    self.posiciones_intrusos = set()

    # Archivo de persistencia de puntajes
    self.archivo_scores = "scores.json"
    self.scores = self.cargar_scores()

    # Fuentes
    self.fuente = pygame.font.SysFont("Segoe UI Emoji", 40)
    self.fuente_texto = pygame.font.SysFont("Arial", 24, bold=True)
    self.fuente_titulo = pygame.font.SysFont("Arial", 48, bold=True)

    # Cargar assets
    self.background = pygame.image.load("fondo.jpg").convert()
    self.background = pygame.transform.scale(
        self.background, (self.ANCHO, self.ALTO)
    )

    self.inicializar_botones()

  def cargar_scores(self):
    """Carga la puntuación máxima asegurando que los valores sean enteros."""
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
    """Guarda las puntuaciones máximas en el archivo JSON."""
    try:
      with open(self.archivo_scores, "w") as f:
        json.dump(self.scores, f, indent=4)
    except Exception as e:
      print(f"Error al guardar scores: {e}")

  def registrar_puntuacion(self, dificultad, puntos):
    """Actualiza la puntuación máxima si la actual la supera."""
    if puntos > self.scores.get(dificultad, 0):
      self.scores[dificultad] = puntos
      self.guardar_scores()

  def inicializar_botones(self):
    self.boton_inicio = boton(self.pantalla, "Jugar")
    self.boton_score = boton(self.pantalla, "Score")
    self.boton_facil = boton(self.pantalla, "Facil")
    self.boton_regresar = boton(self.pantalla, "Regresar")
    self.boton_medio = boton(self.pantalla, "Medio")
    self.boton_dificil = boton(self.pantalla, "Dificil")
    self.boton_extremo = boton(self.pantalla, "Extremo")
    self.boton_salir = boton(self.pantalla, "Salir")
    self.boton_frutas = boton(self.pantalla, "Frutas")
    self.boton_futbol = boton(self.pantalla, "Futbol")
    self.boton_emojis = boton(self.pantalla, "Emojis")

    # Botones específicos para la pantalla Game Over
    self.boton_reiniciar = boton(self.pantalla, "Reiniciar")
    self.boton_score_go = boton(self.pantalla, "Score")
    self.boton_salir1 = boton(self.pantalla, "Salir")

    # Posicionamiento general
    self.boton_inicio.rect.centerx = self.ANCHO // 2
    self.boton_inicio.rect.centery = self.ALTO // 2 - 30

    self.boton_score.rect.centerx = self.ANCHO // 2
    self.boton_score.rect.centery = self.ALTO // 2 + 40

    self.boton_regresar.rect.topleft = (20, 20)
    self.boton_medio.rect.centerx = self.ANCHO // 2
    self.boton_facil.rect.centerx = (self.ANCHO // 2) - 220
    self.boton_dificil.rect.centerx = (self.ANCHO // 2) + 220
    self.boton_extremo.rect.centery = int(self.ALTO // 1.5)
    self.boton_salir.rect.topright = (self.ANCHO - 20, 20)
    self.boton_frutas.rect.centerx = (self.ANCHO // 2) - 220
    self.boton_futbol.rect.centerx = (self.ANCHO // 2) + 220
    self.boton_emojis.rect.centerx = self.ANCHO // 2

    # Posicionamiento vertical ordenado para GAME OVER
    self.boton_reiniciar.rect.centerx = self.ANCHO // 2
    self.boton_reiniciar.rect.centery = self.ALTO // 2 + 20

    self.boton_score_go.rect.centerx = self.ANCHO // 2
    self.boton_score_go.rect.centery = self.ALTO // 2 + 90

    self.boton_salir1.rect.centerx = self.ANCHO // 2
    self.boton_salir1.rect.centery = self.ALTO // 2 + 160

    # Preparar texto en cada botón
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
    if dificultad == "FACIL":
      filas, columnas = 2, 2
    elif dificultad == "MEDIO":
      filas, columnas = 4, 4
    elif dificultad == "DIFICIL":
      filas, columnas = 6, 6
    elif dificultad == "EXTREMO":
      filas, columnas = 8, 8

    cant_intrusos = 1
    cat = random.choice(self.CATEGORIAS[categoria])

    grid = [[cat["normal"] for _ in range(columnas)] for _ in range(filas)]

    posiciones_intrusos = set()
    while len(posiciones_intrusos) < cant_intrusos:
      pos_x = random.randint(0, columnas - 1)
      pos_y = random.randint(0, filas - 1)
      posiciones_intrusos.add((pos_x, pos_y))

    for pos_x, pos_y in posiciones_intrusos:
      grid[pos_y][pos_x] = cat["intruso"]

    return grid, posiciones_intrusos

  def aplicar_penalizacion(self):
    penalizaciones = {
        "FACIL": (5, 0.5),
        "MEDIO": (5, 0.5),
        "DIFICIL": (10, 0.8),
        "EXTREMO": (15, 1.0),
    }
    pts_penal, t_penal = penalizaciones.get(self.dificultad_actual, (5, 0.5))
    self.tiempo_restante = max(0.0, self.tiempo_restante - t_penal)
    self.puntuacion = max(0, self.puntuacion - pts_penal)

  def ejecutar(self):
    ejecutando = True

    while ejecutando:
      dt = self.clock.tick(60) / 1000.0
      self.pantalla.blit(self.background, [0, 0])
      clic = False

      for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
          ejecutando = False
        elif evento.type == pygame.MOUSEBUTTONDOWN:
          if evento.button == 1:
            clic = True
        elif evento.type == pygame.KEYDOWN:
          if evento.key == pygame.K_ESCAPE:
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

      # --- ESTADO: MENU ---
      if self.estado_juego == "MENU":
        titulo = self.fuente_titulo.render(
            "Encuentra al Intruso", True, self.BLANCO
        )
        self.pantalla.blit(
            titulo, (self.ANCHO // 2 - titulo.get_width() // 2, 150)
        )

        self.boton_inicio.dibuja_boton()
        self.boton_score.dibuja_boton()

        if clic:
          if self.boton_inicio.rect.collidepoint(mouse_pos):
            self.estado_juego = "DIFICULTAD"
          elif self.boton_score.rect.collidepoint(mouse_pos):
            self.estado_anterior = "MENU"
            self.estado_juego = "SCORES"

      # --- ESTADO: SCORES ---
      elif self.estado_juego == "SCORES":
        titulo = self.fuente_titulo.render(
            "Puntuaciones Máximas", True, self.BLANCO
        )
        self.pantalla.blit(
            titulo, (self.ANCHO // 2 - titulo.get_width() // 2, 120)
        )

        self.boton_regresar.dibuja_boton()

        y_offset = 220
        encabezado = self.fuente_texto.render(
            f"{'DIFICULTAD':<20} {'PUNTAJE MÁXIMO':<15}", True, self.AMARILLO
        )
        self.pantalla.blit(
            encabezado, (self.ANCHO // 2 - encabezado.get_width() // 2, y_offset)
        )

        y_offset += 50
        for dif in ["FACIL", "MEDIO", "DIFICIL", "EXTREMO"]:
          max_score = self.scores.get(dif, 0)
          linea_txt = f"{dif:<20} {max_score:<15}"
          txt_rendered = self.fuente_texto.render(linea_txt, True, self.BLANCO)
          self.pantalla.blit(
              txt_rendered,
              (self.ANCHO // 2 - txt_rendered.get_width() // 2, y_offset),
          )
          y_offset += 45

        if clic and self.boton_regresar.rect.collidepoint(mouse_pos):
          self.estado_juego = self.estado_anterior

      # --- ESTADO: DIFICULTAD ---
      elif self.estado_juego == "DIFICULTAD":
        titulo = self.fuente_titulo.render("Dificultad", True, self.BLANCO)
        self.pantalla.blit(
            titulo, (self.ANCHO // 2 - titulo.get_width() // 2, 150)
        )

        self.boton_facil.dibuja_boton()
        self.boton_regresar.dibuja_boton()
        self.boton_medio.dibuja_boton()
        self.boton_dificil.dibuja_boton()
        self.boton_extremo.dibuja_boton()

        if clic:
          if self.boton_facil.rect.collidepoint(mouse_pos):
            self.dificultad_actual = "FACIL"
            self.estado_juego = "CATEGORIA"
          elif self.boton_medio.rect.collidepoint(mouse_pos):
            self.dificultad_actual = "MEDIO"
            self.estado_juego = "CATEGORIA"
          elif self.boton_dificil.rect.collidepoint(mouse_pos):
            self.dificultad_actual = "DIFICIL"
            self.estado_juego = "CATEGORIA"
          elif self.boton_extremo.rect.collidepoint(mouse_pos):
            self.dificultad_actual = "EXTREMO"
            self.estado_juego = "CATEGORIA"
          elif self.boton_regresar.rect.collidepoint(mouse_pos):
            self.estado_juego = "MENU"

      # --- ESTADO: CATEGORIA ---
      elif self.estado_juego == "CATEGORIA":
        titulo = self.fuente_titulo.render(
            "Selecciona Categoría", True, self.BLANCO
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
            categoria_elegida = "FRUTAS"
          elif self.boton_futbol.rect.collidepoint(mouse_pos):
            categoria_elegida = "FUTBOL"
          elif self.boton_emojis.rect.collidepoint(mouse_pos):
            categoria_elegida = "EMOJIS"
          elif self.boton_regresar.rect.collidepoint(mouse_pos):
            self.estado_juego = "DIFICULTAD"

          if categoria_elegida:
            self.categoria_seleccionada = categoria_elegida
            self.puntuacion = 0
            self.tiempo_restante = 60.0
            self.grid, self.posiciones_intrusos = self.generar_nivel(
                self.dificultad_actual, self.categoria_seleccionada
            )
            self.estado_juego = "JUGANDO"

      # --- ESTADO: JUGANDO ---
      elif self.estado_juego == "JUGANDO":
        self.boton_salir.dibuja_boton()

        if clic and self.boton_salir.rect.collidepoint(mouse_pos):
          self.registrar_puntuacion(self.dificultad_actual, self.puntuacion)
          self.estado_juego = "GAME_OVER"

        self.tiempo_restante -= dt

        txt_tiempo = self.fuente_texto.render(
            f"Tiempo: {max(0, int(self.tiempo_restante))}s", True, self.BLANCO
        )
        self.pantalla.blit(txt_tiempo, (20, 50))

        if self.tiempo_restante <= 0:
          self.registrar_puntuacion(self.dificultad_actual, self.puntuacion)
          self.estado_juego = "GAME_OVER"

        txt_info = self.fuente_texto.render(
            f"Puntos: {self.puntuacion}", True, self.BLANCO
        )
        self.pantalla.blit(txt_info, (20, 20))

        filas = len(self.grid)
        columnas = len(self.grid[0])

        margen_x, margen_y = 100, 100
        ancho_celda = (self.ANCHO - 2 * margen_x) // columnas
        alto_celda = (self.ALTO - 2 * margen_y) // filas

        area_tablero = pygame.Rect(
            margen_x, margen_y, columnas * ancho_celda, filas * alto_celda
        )
        clic_en_tablero = False

        for r in range(filas):
          for c in range(columnas):
            x = margen_x + c * ancho_celda
            y = margen_y + r * alto_celda
            rect = pygame.Rect(x, y, ancho_celda - 5, alto_celda - 5)

            pygame.draw.rect(
                self.pantalla, (220, 220, 220), rect, border_radius=8
            )

            texto = self.fuente.render(self.grid[r][c], True, self.NEGRO)
            self.pantalla.blit(
                texto,
                (
                    x + (ancho_celda - texto.get_width()) // 2,
                    y + (alto_celda - texto.get_height()) // 2,
                ),
            )

            if clic and rect.collidepoint(mouse_pos):
              clic_en_tablero = True
              if (c, r) in self.posiciones_intrusos:
                self.puntuacion += 20
                bonificacion = (
                    1.5
                    if self.dificultad_actual in ["MEDIO", "FACIL"]
                    else 1.0
                )
                self.tiempo_restante = min(
                    60.0, self.tiempo_restante + bonificacion
                )
                self.grid, self.posiciones_intrusos = self.generar_nivel(
                    self.dificultad_actual, self.categoria_seleccionada
                )
              else:
                self.aplicar_penalizacion()

        if (
            clic
            and not clic_en_tablero
            and not self.boton_salir.rect.collidepoint(mouse_pos)
        ):
          if area_tablero.collidepoint(mouse_pos):
            self.aplicar_penalizacion()

      # --- ESTADO: GAME OVER ---
      elif self.estado_juego == "GAME_OVER":
        txt_fin = self.fuente_titulo.render("JUEGO TERMINADO", True, self.ROJO)
        txt_mensaje = self.fuente_texto.render(
            "Muy bien, ¿deseas reiniciar el juego?", True, self.BLANCO
        )
        txt_puntos = self.fuente_texto.render(
            f"Puntuación Final: {self.puntuacion}", True, self.AMARILLO
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

        # Renderizado de botones
        self.boton_reiniciar.dibuja_boton()
        self.boton_score_go.dibuja_boton()
        self.boton_salir1.dibuja_boton()

        if clic:
          if self.boton_reiniciar.rect.collidepoint(mouse_pos):
            self.puntuacion = 0
            self.tiempo_restante = 60.0
            self.grid, self.posiciones_intrusos = self.generar_nivel(
                self.dificultad_actual, self.categoria_seleccionada
            )
            self.estado_juego = "JUGANDO"
          elif self.boton_score_go.rect.collidepoint(mouse_pos):
            self.estado_anterior = "GAME_OVER"
            self.estado_juego = "SCORES"
          elif self.boton_salir1.rect.collidepoint(mouse_pos):
            self.puntuacion = 0
            self.estado_juego = "MENU"

      pygame.display.flip()

    pygame.quit()


def main():
  juego = JuegoIntruso()
  juego.ejecutar()


if __name__ == "__main__":
  main()