import numpy as np
import time
import threading
import random
from typing import Tuple, List, Optional
from enum import Enum

class Direction(Enum):
    """Directions possibles pour le serpent"""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class SnakeGame:
    """Jeu Snake optimisé pour l'affichage LED"""
    
    def __init__(self, width=128, height=128):
        self.width = width
        self.height = height
        self.running = False
        self.paused = False
        self.thread = None
        self.game_over = False
        
        # Paramètres du jeu
        self.FPS = 4  # Vitesse plus lente pour un meilleur gameplay
        self.BLOCK_SIZE = 4  # Taille des blocs en pixels (4x4)
        self.INITIAL_LENGTH = 1  # Nombre de blocs pour le serpent initial

        # État du serpent
        self.snake = []  # Liste de positions (x, y) pour chaque bloc du serpent
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT

        # Nourriture
        self.food = (0, 0)  # Position du bloc de nourriture
        
        # Score et statistiques
        self.score = 0
        self.high_score = 0
        self.moves_without_food = 0
        self.max_moves_without_food = 200  # Éviter les boucles infinies
        
        # Contrôles
        self.keys_pressed = set()
        self.control_thread = None
        
        # Frame actuelle
        self.current_frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Couleurs
        self.snake_head_color = (0, 255, 0)      # Vert vif pour la tête
        self.snake_body_color = (0, 180, 0)      # Vert plus sombre pour le corps
        self.snake_tail_color = (0, 120, 0)      # Vert encore plus sombre pour la queue
        self.food_color = (255, 50, 50)          # Rouge pour la nourriture
        self.special_food_color = (255, 215, 0)  # Or pour la nourriture spéciale
        self.background_color = (0, 0, 0)        # Noir
        self.game_over_color = (255, 255, 0)     # Jaune pour Game Over
        
        # Effets visuels
        self.food_pulse = 0.0
        self.food_pulse_speed = 0.3
        
        # Types de nourriture
        self.food_type = "normal"  # "normal" ou "special"
        self.special_food_chance = 0.1  # 10% de chance d'avoir de la nourriture spéciale
        
        # Chiffres pour l'affichage des scores (3x5 pixels)
        self.DIGITS = {
            0: ["111", "101", "101", "101", "111"],
            1: ["010", "110", "010", "010", "111"],
            2: ["111", "001", "111", "100", "111"],
            3: ["111", "001", "111", "001", "111"],
            4: ["101", "101", "111", "001", "001"],
            5: ["111", "100", "111", "001", "111"],
            6: ["111", "100", "111", "101", "111"],
            7: ["111", "001", "010", "010", "010"],
            8: ["111", "101", "111", "101", "111"],
            9: ["111", "101", "111", "001", "111"],
        }
        
        # Lettres pour "GAME OVER" et "SCORE"
        self.LETTERS = {
            'G': ["1111", "1000", "1011", "1001", "1111"],
            'A': ["0111", "1001", "1111", "1001", "1001"],
            'M': ["1001", "1111", "1111", "1001", "1001"],
            'E': ["1111", "1000", "1110", "1000", "1111"],
            'O': ["0111", "1001", "1001", "1001", "0111"],
            'V': ["1001", "1001", "1001", "0110", "0110"],
            'R': ["1110", "1001", "1110", "1010", "1001"],
            'S': ["0111", "1000", "0110", "0001", "1110"],
            'C': ["0111", "1000", "1000", "1000", "0111"],
            ' ': ["0000", "0000", "0000", "0000", "0000"],
            ':': ["0000", "0100", "0000", "0100", "0000"],
        }
        
        self.reset_game()
    
    def reset_game(self):
        """Remet à zéro le jeu"""
        # Calculer la position centrale pour le bloc de 4x4
        center_x = (self.width // 2) - (self.BLOCK_SIZE // 2)
        center_y = (self.height // 2) - (self.BLOCK_SIZE // 2)

        # Initialiser le serpent avec un bloc de 4x4 au centre
        self.snake = [(center_x, center_y)]  # Un seul bloc pour commencer
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT

        # Placer la première nourriture
        self._generate_food()

        # Réinitialiser les statistiques
        self.score = 0
        self.moves_without_food = 0
        self.game_over = False
        self.food_pulse = 0.0
    
    def start_game(self):
        """Démarre le jeu (version pour UI)"""
        # Arrêter tout thread existant
        if self.control_thread and self.control_thread.is_alive():
            self.running = False
            self.control_thread.join(timeout=0.5)

        # Démarrer le jeu
        self.running = True
        self.paused = False
        # NE PAS toucher à game_over ici - il est géré par reset_game()

        # Démarrer le thread de contrôle
        self.control_thread = threading.Thread(target=self._control_loop, daemon=True)
        self.control_thread.start()

    def stop_game(self):
        """Arrête le jeu (version pour UI)"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.5)
        if self.control_thread:
            self.control_thread.join(timeout=0.5)

    def pause_game(self):
        """Met en pause le jeu (version pour UI)"""
        self.paused = True

    def resume_game(self):
        """Reprend le jeu (version pour UI)"""
        if not self.game_over:
            self.paused = False

    def start(self):
        """Démarre le jeu (version threadée)"""
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
        """Arrête le jeu (version threadée)"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.5)
        if self.control_thread:
            self.control_thread.join(timeout=0.5)

    def pause(self):
        """Met en pause le jeu (version threadée)"""
        self.paused = True

    def resume(self):
        """Reprend le jeu (version threadée)"""
        if not self.game_over:
            self.paused = False
    
    def restart(self):
        """Redémarre le jeu"""
        self.reset_game()
        if not self.running:
            self.start()
    
    def set_key_pressed(self, key: str, pressed: bool):
        """Met à jour l'état des touches"""
        if pressed:
            self.keys_pressed.add(key)
        else:
            self.keys_pressed.discard(key)
    
    def _control_loop(self):
        """Boucle de gestion des contrôles"""
        while self.running:
            # Gestion des directions (ZQSD pour clavier français)
            if 'z' in self.keys_pressed or 'up' in self.keys_pressed:
                self._change_direction(Direction.UP)
            elif 's' in self.keys_pressed or 'down' in self.keys_pressed:
                self._change_direction(Direction.DOWN)
            elif 'q' in self.keys_pressed or 'left' in self.keys_pressed:
                self._change_direction(Direction.LEFT)
            elif 'd' in self.keys_pressed or 'right' in self.keys_pressed:
                self._change_direction(Direction.RIGHT)
            
            time.sleep(1 / 30)  # 30 FPS pour les contrôles
    
    def change_direction(self, new_direction: Direction):
        """Change la direction du serpent (évite les retours en arrière)"""
        self._change_direction(new_direction)

    def _change_direction(self, new_direction: Direction):
        """Change la direction du serpent (évite les retours en arrière)"""
        # Empêcher le serpent de revenir sur lui-même
        opposite = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }

        if new_direction != opposite.get(self.direction):
            self.next_direction = new_direction
    
    def update(self):
        """Met à jour le jeu (pour utilisation avec timer UI)"""
        if not self.running:
            return

        # Si le jeu est en pause, on continue quand même à dessiner pour montrer l'état actuel
        if self.paused:
            self._draw_frame()
            return

        # Si le jeu est terminé, on affiche l'écran Game Over
        if self.game_over:
            self._update_effects()  # Pour les effets visuels de l'écran Game Over
            self._draw_frame()
            return

        current_time = time.time()
        move_interval = 1.0 / self.FPS

        # Vérifier si c'est le moment de bouger
        if not hasattr(self, 'last_move_time'):
            self.last_move_time = current_time

        if current_time - self.last_move_time >= move_interval:
            self._update_game()
            self.last_move_time = current_time

            # Accélération progressive du jeu
            if self.score > 0 and self.score % 50 == 0:
                self.FPS = min(15, self.FPS + 0.5)

        self._update_effects()
        self._draw_frame()

    def _game_loop(self):
        """Boucle principale du jeu (pour utilisation avec threads)"""
        self.last_move_time = time.time()
        move_interval = 1.0 / self.FPS

        while self.running:
            current_time = time.time()

            if not self.paused and not self.game_over:
                if current_time - self.last_move_time >= move_interval:
                    self._update_game()
                    self.last_move_time = current_time

                    # Accélération progressive du jeu
                    if self.score > 0 and self.score % 50 == 0:
                        self.FPS = min(15, self.FPS + 0.5)

            self._update_effects()
            self._draw_frame()
            time.sleep(1 / 30)  # 30 FPS pour le rendu
    
    def _update_game(self):
        """Met à jour la logique du jeu"""
        if self.game_over:
            return

        # Mettre à jour la direction
        self.direction = self.next_direction

        # Calculer la nouvelle position de la tête (coin supérieur gauche du bloc)
        head_x, head_y = self.snake[0]
        dx, dy = self.direction.value
        new_head_x = head_x + dx * self.BLOCK_SIZE
        new_head_y = head_y + dy * self.BLOCK_SIZE
        new_head = (new_head_x, new_head_y)

        # Vérifier les collisions avec les murs
        if (new_head_x < 0 or new_head_x + self.BLOCK_SIZE > self.width or
            new_head_y < 0 or new_head_y + self.BLOCK_SIZE > self.height):
            self._game_over()
            return

        # Vérifier les collisions avec le corps (vérifier si le nouveau bloc chevauche un bloc existant)
        for i, (snake_x, snake_y) in enumerate(self.snake):
            if (new_head_x < snake_x + self.BLOCK_SIZE and new_head_x + self.BLOCK_SIZE > snake_x and
                new_head_y < snake_y + self.BLOCK_SIZE and new_head_y + self.BLOCK_SIZE > snake_y):
                self._game_over()
                return

        # Ajouter la nouvelle tête
        self.snake.insert(0, new_head)

        # Vérifier si la nourriture est mangée (vérifier si le bloc tête chevauche le bloc nourriture)
        food_x, food_y = self.food
        if (new_head_x < food_x + self.BLOCK_SIZE and new_head_x + self.BLOCK_SIZE > food_x and
            new_head_y < food_y + self.BLOCK_SIZE and new_head_y + self.BLOCK_SIZE > food_y):
            self._eat_food()
        else:
            # Retirer la queue
            self.snake.pop()
            self.moves_without_food += 1

            # Vérifier si le serpent tourne en rond trop longtemps
            if self.moves_without_food > self.max_moves_without_food:
                self._game_over()
    
    def _eat_food(self):
        """Gère la consommation de nourriture"""
        if self.food_type == "special":
            # Nourriture spéciale : plus de points et croissance double (deux blocs)
            self.score += 20
            # Ajouter deux segments supplémentaires (2 blocs de 4x4)
            tail = self.snake[-1]
            self.snake.append(tail)
            self.snake.append(tail)
        else:
            # Nourriture normale : ajouter un bloc de 4x4
            self.score += 10
            # Ne pas retirer la queue cette fois (le serpent grandit)

        # Mettre à jour le meilleur score
        if self.score > self.high_score:
            self.high_score = self.score

        # Réinitialiser le compteur de mouvements
        self.moves_without_food = 0

        # Générer une nouvelle nourriture
        self._generate_food()
    
    def _generate_food(self):
        """Génère une nouvelle nourriture à une position libre (bloc 4x4)"""
        max_attempts = 100
        attempts = 0

        while attempts < max_attempts:
            # Générer une position pour le coin supérieur gauche du bloc 4x4
            x = random.randint(0, self.width - self.BLOCK_SIZE)
            y = random.randint(0, self.height - self.BLOCK_SIZE)

            # Vérifier que le bloc ne se superpose pas avec le serpent
            block_occupied = False
            for snake_x, snake_y in self.snake:
                # Vérifier si le bloc de nourriture chevauche le bloc du serpent
                if (x < snake_x + self.BLOCK_SIZE and x + self.BLOCK_SIZE > snake_x and
                    y < snake_y + self.BLOCK_SIZE and y + self.BLOCK_SIZE > snake_y):
                    block_occupied = True
                    break

            if not block_occupied:
                self.food = (x, y)

                # Déterminer le type de nourriture
                self.food_type = "special" if random.random() < self.special_food_chance else "normal"

                # Réinitialiser l'animation de pulsation
                self.food_pulse = 0.0
                return

            attempts += 1

        # Si aucune position libre n'est trouvée, le jeu est gagné !
        self._game_over()
    
    def _game_over(self):
        """Termine le jeu"""
        self.game_over = True
        # Forcer un dernier dessin pour afficher immédiatement le game over
        self._update_effects()
        self._draw_frame()
    
    def _update_effects(self):
        """Met à jour les effets visuels"""
        # Animation de pulsation de la nourriture
        self.food_pulse += self.food_pulse_speed
        if self.food_pulse > 2 * np.pi:
            self.food_pulse = 0.0
    
    def _draw_frame(self):
        """Dessine la frame actuelle"""
        # Effacer la frame
        self.current_frame.fill(0)
        
        if self.game_over:
            self._draw_game_over()
        else:
            # Dessiner le serpent avec dégradé de couleur
            self._draw_snake()
            
            # Dessiner la nourriture avec effet de pulsation
            self._draw_food()
            
            # Dessiner le score
            self._draw_score()
    
    def _draw_snake(self):
        """Dessine le serpent avec des blocs de 4x4 LEDs"""
        snake_length = len(self.snake)

        for i, (block_x, block_y) in enumerate(self.snake):
            # Dessiner un bloc de 4x4 LEDs pour chaque segment du serpent
            if i == 0:
                # Tête du serpent - couleur vive avec effet de brillance
                color = self.snake_head_color
                enhanced_color = tuple(min(255, c + 30) for c in color)
            else:
                # Corps du serpent - dégradé vers la queue
                progress = i / (snake_length - 1) if snake_length > 1 else 0

                # Interpolation entre la couleur du corps et de la queue
                body_r, body_g, body_b = self.snake_body_color
                tail_r, tail_g, tail_b = self.snake_tail_color

                r = int(body_r * (1 - progress) + tail_r * progress)
                g = int(body_g * (1 - progress) + tail_g * progress)
                b = int(body_b * (1 - progress) + tail_b * progress)
                enhanced_color = (r, g, b)

            # Dessiner le bloc 4x4
            for dx in range(self.BLOCK_SIZE):
                for dy in range(self.BLOCK_SIZE):
                    x = block_x + dx
                    y = block_y + dy
                    if 0 <= x < self.width and 0 <= y < self.height:
                        self.current_frame[y, x] = enhanced_color
    
    def _draw_food(self):
        """Dessine la nourriture avec des blocs de 4x4 LEDs et effet de pulsation"""
        block_x, block_y = self.food

        # Effet de pulsation
        pulse_factor = 0.8 + 0.4 * np.sin(self.food_pulse)

        if self.food_type == "special":
            base_color = self.special_food_color
            # Effet scintillant pour la nourriture spéciale
            if int(time.time() * 10) % 2:
                pulse_factor *= 1.2
        else:
            base_color = self.food_color

        # Appliquer l'effet de pulsation
        color = tuple(int(c * pulse_factor) for c in base_color)
        color = tuple(min(255, max(0, c)) for c in color)

        # Dessiner le bloc de 4x4 LEDs pour la nourriture
        for dx in range(self.BLOCK_SIZE):
            for dy in range(self.BLOCK_SIZE):
                x = block_x + dx
                y = block_y + dy
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.current_frame[y, x] = color

        # Effet de halo pour la nourriture spéciale
        if self.food_type == "special":
            halo_size = 2  # Taille du halo autour du bloc
            for dx in range(-halo_size, self.BLOCK_SIZE + halo_size):
                for dy in range(-halo_size, self.BLOCK_SIZE + halo_size):
                    # Ne pas appliquer le halo sur le bloc lui-même
                    if 0 <= dx < self.BLOCK_SIZE and 0 <= dy < self.BLOCK_SIZE:
                        continue

                    hx, hy = block_x + dx, block_y + dy
                    if 0 <= hx < self.width and 0 <= hy < self.height:
                        # Ajouter un halo subtil
                        current = self.current_frame[hy, hx]
                        halo = tuple(min(255, int(c) + 10) for c in current)
                        self.current_frame[hy, hx] = halo
    
    def _draw_score(self):
        """Dessine le score actuel"""
        # Score en haut à gauche
        score_str = str(self.score)
        x_pos = 2
        y_pos = 2
        
        for i, digit_char in enumerate(score_str):
            if digit_char.isdigit():
                digit = int(digit_char)
                self._draw_digit(digit, x_pos + i * 4, y_pos, (255, 255, 255))
        
        # Meilleur score en haut à droite (si différent du score actuel)
        if self.high_score > self.score:
            high_score_str = str(self.high_score)
            x_pos = self.width - len(high_score_str) * 4 - 2
            y_pos = 2
            
            for i, digit_char in enumerate(high_score_str):
                if digit_char.isdigit():
                    digit = int(digit_char)
                    self._draw_digit(digit, x_pos + i * 4, y_pos, (255, 255, 0))
    
    def _draw_game_over(self):
        """Dessine l'écran Game Over"""
        # Fond semi-transparent
        overlay = self.current_frame.astype(np.float32)
        overlay *= 0.3
        self.current_frame = overlay.astype(np.uint8)

        # Position centrale
        center_x = self.width // 2
        center_y = self.height // 2

        # "GAME OVER" - Texte plus grand et visible
        game_over_text = "GAME OVER"
        text_width = len(game_over_text) * 5
        start_x = (self.width - text_width) // 2
        start_y = center_y - 15

        for i, char in enumerate(game_over_text):
            if char in self.LETTERS:
                self._draw_letter(char, start_x + i * 5, start_y, self.game_over_color)

        # Score final
        score_text = f"SCORE: {self.score}"
        start_x = (self.width - len(score_text) * 4) // 2
        start_y = center_y - 5

        for i, char in enumerate(score_text):
            if char.isdigit():
                self._draw_digit(int(char), start_x + i * 4, start_y, (255, 255, 255))
            elif char in self.LETTERS:
                self._draw_letter(char, start_x + i * 4, start_y, (255, 255, 255))

        # Meilleur score
        if self.high_score > 0:
            best_text = f"BEST: {self.high_score}"
            start_x = (self.width - len(best_text) * 4) // 2
            start_y = center_y + 5

            for i, char in enumerate(best_text):
                if char.isdigit():
                    self._draw_digit(int(char), start_x + i * 4, start_y, (255, 255, 0))
                elif char in self.LETTERS:
                    self._draw_letter(char, start_x + i * 4, start_y, (255, 255, 0))

        # Instructions pour rejouer
        if self.width >= 64:  # Seulement si l'écran est assez large
            play_text = "PRESS START"
            start_x = (self.width - len(play_text) * 4) // 2
            start_y = center_y + 15

            for i, char in enumerate(play_text):
                if char in self.LETTERS:
                    self._draw_letter(char, start_x + i * 4, start_y, (200, 200, 200))
    
    def _draw_digit(self, digit: int, x: int, y: int, color: Tuple[int, int, int]):
        """Dessine un chiffre 3x5"""
        if digit not in self.DIGITS:
            return
            
        pattern = self.DIGITS[digit]
        for row in range(5):
            for col in range(3):
                if row < len(pattern) and col < len(pattern[row]) and pattern[row][col] == '1':
                    px = x + col
                    py = y + row
                    if 0 <= px < self.width and 0 <= py < self.height:
                        self.current_frame[py, px] = color
    
    def _draw_letter(self, letter: str, x: int, y: int, color: Tuple[int, int, int]):
        """Dessine une lettre"""
        if letter not in self.LETTERS:
            return
            
        pattern = self.LETTERS[letter]
        for row in range(len(pattern)):
            for col in range(len(pattern[row])):
                if pattern[row][col] == '1':
                    px = x + col
                    py = y + row
                    if 0 <= px < self.width and 0 <= py < self.height:
                        self.current_frame[py, px] = color
    
    def get_frame(self) -> np.ndarray:
        """Retourne la frame actuelle du jeu"""
        return self.current_frame.copy()
    
    def get_score(self) -> int:
        """Retourne le score actuel"""
        return self.score
    
    def get_high_score(self) -> int:
        """Retourne le meilleur score"""
        return self.high_score
    
    def get_snake_length(self) -> int:
        """Retourne la longueur actuelle du serpent (en nombre de blocs)"""
        return len(self.snake)
    
    def is_game_over(self) -> bool:
        """Vérifie si le jeu est terminé"""
        return self.game_over
    
    def is_running(self) -> bool:
        """Vérifie si le jeu a été démarré et pas arrêté (même en Game Over)"""
        return self.running

    def is_actively_playing(self) -> bool:
        """Vérifie si le jeu est en cours ET pas en game over"""
        return self.running and not self.game_over
    
    def is_paused(self) -> bool:
        """Vérifie si le jeu est en pause"""
        return self.paused
    
    def get_game_stats(self) -> dict:
        """Retourne les statistiques du jeu"""
        return {
            "score": self.score,
            "high_score": self.high_score,
            "length": len(self.snake),
            "fps": self.FPS,
            "food_type": self.food_type,
            "moves_without_food": self.moves_without_food,
            "game_over": self.game_over,
            "paused": self.paused
        }