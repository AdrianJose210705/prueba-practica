import pygame.font

class boton:
    def __init__(self, pantalla_juego, texto):
        self.screen = pantalla_juego
        self.screen_rect = self.screen.get_rect()
        self.width, self.height = 200, 50
        self.color = (255, 0, 0)
        self.textocolor = (255, 255, 255)
        
        self.font = pygame.font.SysFont(None, 48)
        
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.screen_rect.center
        
        self.prepara_texto(texto)
    
    def prepara_texto(self, texto):
        self.texto_image = self.font.render(texto, True, self.textocolor, self.color)
        self.texto_image_rect = self.texto_image.get_rect()
        self.texto_image_rect.center = self.rect.center
        
    def dibuja_boton(self):
        self.screen.fill(self.color, self.rect)
        self.screen.blit(self.texto_image, self.texto_image_rect)