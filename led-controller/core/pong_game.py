import numpy as np
import time
import threading
from typing import Tuple, Optional

class PongGame:
    """Jeu Pong optimisé pour l'affichage LED"""
    
    def __init__(self, width=128, height=128):
        self.width = width
        self.height = height
        self.running = False
        self.paused = False
        self.thread = None
        self.game_over = False
        self.winner = None  # 'left' ou 'right'
        
        # Paramètres du jeu
        self.PADDLE_HEIGHT = 20
        self.PADDLE_WIDTH = 3
        self.BALL_SIZE = 3
        self.FPS = 30
        
        # Positions initiales
        self.left_paddle_y = height // 2 - self.PADDLE_HEIGHT // 2
        self.right_paddle_y = height // 2 - self.PADDLE_HEIGHT // 2
        self.ball_x = width // 2
        self.ball_y = height // 2
        self.ball_dx = 2
        self.ball_dy = 1
        
        # Scores
        self.left_score = 0
        self.right_score = 0
        
        # Contrôles
        self.keys_pressed = set()
        self.control_thread = None
        
        # Frame actuelle
        self.current_frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Chiffres pour l'affichage des scores
        self.DIGITS = {
            "0": ["111", "101", "101", "101", "111"],
            "1": ["010", "110", "010", "010", "111"],
            "2": ["111", "001", "111", "100", "111"],
            "3": ["111", "001", "111", "001", "111"],
            "4": ["101", "101", "111", "001", "001"],
            "5": ["111", "100", "111", "001", "111"],
            "6": ["111", "100", "111", "101", "111"],
            "7": ["111", "001", "010", "010", "010"],
            "8": ["111", "101", "111", "101", "111"],
            "9": ["111", "101", "111", "001", "111"],
        }
        
        # Lettres pour "GAME OVER"
        self.LETTERS = {
            "G": ["1111", "1000", "1011", "1001", "1111"],
            "A": ["010", "101", "111", "101", "101"],
            "M": ["101", "111", "111", "101", "101"],
            "E": ["111", "100", "111", "100", "111"],
            "O": ["111", "101", "101", "101", "111"],
            "V": ["101", "101", "101", "101", "010"],
            "R": ["111", "101", "111", "110", "101"],
        }
    
    def start(self):
        """Démarre le jeu"""
        if self.running:
            return
            
        self.running = True
        self.paused = False
        self.thread = threading.Thread(target=self._game_loop, daemon=True)
        self.thread.start()
        
        # Démarrer le thread de contrôle
        self.control_thread = threading.Thread(target=self._control_loop, daemon=True)
        self.control_thread.start()
    
    def stop(self):
        """Arrête le jeu"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.5)
        if self.control_thread:
            self.control_thread.join(timeout=0.5)
    
    def pause(self):
        """Met en pause le jeu"""
        self.paused = True
    
    def resume(self):
        """Reprend le jeu"""
        self.paused = False
    
    def reset(self):
        """Remet à zéro le jeu"""
        self.left_score = 0
        self.right_score = 0
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        self.ball_dx = 2
        self.ball_dy = 1
        self.left_paddle_y = self.height // 2 - self.PADDLE_HEIGHT // 2
        self.right_paddle_y = self.height // 2 - self.PADDLE_HEIGHT // 2
        self.game_over = False
        self.winner = None
    
    def set_key_pressed(self, key: str, pressed: bool):
        """Met à jour l'état des touches"""
        if pressed:
            self.keys_pressed.add(key)
        else:
            self.keys_pressed.discard(key)
    
    def _control_loop(self):
        """Boucle de gestion des contrôles"""
        while self.running:
            # Mise à jour des raquettes basée sur les touches pressées
            if 'w' in self.keys_pressed:
                self.left_paddle_y = max(0, self.left_paddle_y - 3)
            if 's' in self.keys_pressed:
                self.left_paddle_y = min(self.height - self.PADDLE_HEIGHT, self.left_paddle_y + 3)
            if 'o' in self.keys_pressed:
                self.right_paddle_y = max(0, self.right_paddle_y - 3)
            if 'l' in self.keys_pressed:
                self.right_paddle_y = min(self.height - self.PADDLE_HEIGHT, self.right_paddle_y + 3)
            
            time.sleep(1 / 60)  # 60 FPS pour les contrôles
    
    def _game_loop(self):
        """Boucle principale du jeu"""
        while self.running:
            if not self.paused:
                self._update_game()
                self._draw_frame()
            
            time.sleep(1 / self.FPS)
    
    def _update_game(self):
        """Met à jour la logique du jeu"""
        # Arrêter le jeu si Game Over
        if self.game_over:
            return
            
        # Déplacement de la balle
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        
        # Rebonds haut/bas
        if self.ball_y <= 0 or self.ball_y >= self.height - self.BALL_SIZE:
            self.ball_dy *= -1
            self.ball_y = max(0, min(self.height - self.BALL_SIZE, self.ball_y))
        
        # Collision avec la raquette gauche
        if self.ball_x <= self.PADDLE_WIDTH:
            if self.left_paddle_y <= self.ball_y <= self.left_paddle_y + self.PADDLE_HEIGHT:
                self.ball_dx *= -1
                self.ball_x = self.PADDLE_WIDTH + 1
                # Effet de rebond selon l'endroit où la balle touche la raquette
                self._adjust_ball_angle(self.ball_y - self.left_paddle_y)
            else:
                self.right_score += 1
                if self.right_score >= 9:
                    self.game_over = True
                    self.winner = 'right'
                self._reset_ball()
        
        # Collision avec la raquette droite
        if self.ball_x >= self.width - self.PADDLE_WIDTH - self.BALL_SIZE:
            if self.right_paddle_y <= self.ball_y <= self.right_paddle_y + self.PADDLE_HEIGHT:
                self.ball_dx *= -1
                self.ball_x = self.width - self.PADDLE_WIDTH - self.BALL_SIZE - 1
                # Effet de rebond selon l'endroit où la balle touche la raquette
                self._adjust_ball_angle(self.ball_y - self.right_paddle_y)
            else:
                self.left_score += 1
                if self.left_score >= 9:
                    self.game_over = True
                    self.winner = 'left'
                self._reset_ball()
    
    def _adjust_ball_angle(self, hit_position: int):
        """Ajuste l'angle de la balle selon l'endroit où elle touche la raquette"""
        # Normaliser la position de frappe (0 à 1)
        normalized_hit = hit_position / self.PADDLE_HEIGHT
        
        # Ajuster la vitesse Y selon la position de frappe
        angle_factor = (normalized_hit - 0.5) * 2  # -1 à 1
        self.ball_dy = int(angle_factor * 2)
        
        # Limiter la vitesse
        self.ball_dy = max(-3, min(3, self.ball_dy))
    
    def _reset_ball(self):
        """Remet la balle au centre"""
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        self.ball_dx = 2 if np.random.random() > 0.5 else -2
        self.ball_dy = np.random.choice([-1, 1])
        time.sleep(1)  # Pause avant de relancer
    
    def _draw_frame(self):
        """Dessine la frame actuelle"""
        # Effacer la frame
        self.current_frame.fill(0)
        
        if self.game_over:
            # Afficher "GAME OVER" et le score final
            self._draw_game_over()
        else:
            # Dessiner les raquettes
            self._draw_paddle(0, self.left_paddle_y, (0, 255, 0))  # Gauche - Vert
            self._draw_paddle(self.width - self.PADDLE_WIDTH, self.right_paddle_y, (0, 255, 0))  # Droite - Vert
            
            # Dessiner la balle (sphérique)
            self._draw_ball(self.ball_x, self.ball_y, (255, 0, 0))  # Rouge
            
            # Dessiner les scores
            self._draw_digit(self.left_score, 5, 5, (255, 255, 255))
            self._draw_digit(self.right_score, self.width - 10, 5, (255, 255, 255))
            
            # Dessiner la ligne centrale
            self._draw_center_line()
    
    def _draw_paddle(self, x: int, y: int, color: Tuple[int, int, int]):
        """Dessine une raquette rectangulaire"""
        for i in range(self.PADDLE_HEIGHT):
            for j in range(self.PADDLE_WIDTH):
                px = x + j
                py = y + i
                if 0 <= px < self.width and 0 <= py < self.height:
                    self.current_frame[py, px] = color
    
    def _draw_ball(self, x: int, y: int, color: Tuple[int, int, int]):
        """Dessine une balle sphérique"""
        radius = self.BALL_SIZE // 2
        for i in range(-radius, radius + 1):
            for j in range(-radius, radius + 1):
                # Créer un effet circulaire
                if i*i + j*j <= radius*radius:
                    px = x + j
                    py = y + i
                    if 0 <= px < self.width and 0 <= py < self.height:
                        # Effet d'éclairage pour donner un aspect 3D
                        distance = np.sqrt(i*i + j*j) / radius
                        intensity = 1.0 - distance * 0.3
                        shaded_color = tuple(int(c * intensity) for c in color)
                        self.current_frame[py, px] = shaded_color
    
    def _draw_digit(self, digit: int, x: int, y: int, color: Tuple[int, int, int]):
        """Dessine un chiffre"""
        pattern = self.DIGITS.get(str(digit), self.DIGITS["0"])
        for row in range(5):
            for col in range(3):
                if pattern[row][col] == "1":
                    px = x + col
                    py = y + row
                    if 0 <= px < self.width and 0 <= py < self.height:
                        self.current_frame[py, px] = color
    
    def _draw_center_line(self):
        """Dessine la ligne centrale pointillée"""
        center_x = self.width // 2
        for y in range(0, self.height, 8):  # Points espacés
            for i in range(4):  # Longueur de chaque point
                if y + i < self.height:
                    self.current_frame[y + i, center_x] = (100, 100, 100)
    
    def _draw_game_over(self):
        """Dessine l'écran Game Over avec le score final"""
        # Afficher "GAME OVER" au centre
        game_over_text = "GAME OVER"
        start_x = (self.width - len(game_over_text) * 5) // 2
        start_y = self.height // 2 - 10
        
        for i, letter in enumerate(game_over_text):
            if letter in self.LETTERS:
                self._draw_letter(letter, start_x + i * 5, start_y, (255, 0, 0))  # Rouge
        
        # Afficher le score final
        score_text = f"{self.left_score} - {self.right_score}"
        score_x = (self.width - len(score_text) * 4) // 2
        score_y = start_y + 8
        
        for i, char in enumerate(score_text):
            if char.isdigit():
                self._draw_digit(int(char), score_x + i * 4, score_y, (255, 255, 255))
            elif char == '-':
                # Dessiner un tiret
                for j in range(3):
                    if score_x + i * 4 + j < self.width and score_y + 2 < self.height:
                        self.current_frame[score_y + 2, score_x + i * 4 + j] = (255, 255, 255)
    
    def _draw_letter(self, letter: str, x: int, y: int, color: Tuple[int, int, int]):
        """Dessine une lettre"""
        pattern = self.LETTERS.get(letter, [])
        for row in range(len(pattern)):
            for col in range(len(pattern[row])):
                if pattern[row][col] == "1":
                    px = x + col
                    py = y + row
                    if 0 <= px < self.width and 0 <= py < self.height:
                        self.current_frame[py, px] = color
    
    def get_frame(self) -> np.ndarray:
        """Retourne la frame actuelle du jeu"""
        return self.current_frame.copy()
    
    def get_score(self) -> Tuple[int, int]:
        """Retourne le score actuel"""
        return (self.left_score, self.right_score)
    
    def is_game_over(self) -> bool:
        """Vérifie si le jeu est terminé"""
        return self.game_over
    
    def get_winner(self) -> Optional[str]:
        """Retourne le gagnant ('left' ou 'right') ou None si pas de Game Over"""
        return self.winner
    
    def restart_game(self):
        """Redémarre le jeu après Game Over"""
        self.reset()
        if not self.running:
            self.start() 