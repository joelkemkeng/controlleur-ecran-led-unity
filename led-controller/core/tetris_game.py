import numpy as np
import time
import threading
import random
from typing import Tuple

class TetrisGame:
    """
    Implémentation complète du jeu Tetris pour affichage LED.
    Adapté aux contraintes de l'écran 128x128 pixels.
    """

    # Définition des pièces Tetris (Tetris pieces)
    SHAPES = [
        # I-piece (ligne)
        [[[1, 1, 1, 1]], [[1], [1], [1], [1]]],
        # O-piece (carré)
        [[[1, 1], [1, 1]]],
        # T-piece (T)
        [[[0, 1, 0], [1, 1, 1]], [[1, 0], [1, 1], [1, 0]], [[1, 1, 1], [0, 1, 0]], [[0, 1], [1, 1], [0, 1]]],
        # S-piece (S)
        [[[0, 1, 1], [1, 1, 0]], [[1, 0], [1, 1], [0, 1]]],
        # Z-piece (Z)
        [[[1, 1, 0], [0, 1, 1]], [[0, 1], [1, 1], [1, 0]]],
        # J-piece (J)
        [[[1, 0, 0], [1, 1, 1]], [[1, 1], [1, 0], [1, 0]], [[1, 1, 1], [0, 0, 1]], [[0, 1], [0, 1], [1, 1]]],
        # L-piece (L)
        [[[0, 0, 1], [1, 1, 1]], [[1, 0], [1, 0], [1, 1]], [[1, 1, 1], [1, 0, 0]], [[1, 1], [0, 1], [0, 1]]]
    ]

    # Couleurs pour chaque pièce
    COLORS = [
        (0, 255, 255),   # Cyan pour I
        (255, 255, 0),   # Jaune pour O
        (200, 0, 255),   # Violet vif pour T
        (0, 255, 0),     # Vert pour S
        (255, 0, 0),     # Rouge pour Z
        (0, 0, 255),     # Bleu pour J
        (255, 165, 0)    # Orange pour L
    ]

    def __init__(self, width=128, height=128):
        self.width = width
        self.height = height
        self.running = False
        self.paused = False
        self.game_over = False
        self.thread = None
        self.control_thread = None
        self.keys_pressed = set()

        # Statistiques du jeu
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.lines_cleared = 0

        # Paramètres du plateau de jeu
        self.cell_size = 6  # Chaque cellule fait 6x6 pixels LED

        # Dimensions du plateau rectangulaire (calculées pour s'adapter aux 128x128 pixels)
        # Largeur réduite pour un aspect plus classique de Tetris
        self.board_width = 10  # 10 colonnes (largeur réduite)
        self.board_height = 16  # 16 lignes (hauteur maintenue)
        
        # Calculer les offsets pour centrer le plateau
        total_board_width = self.board_width * self.cell_size
        total_board_height = self.board_height * self.cell_size
        self.offset_x = (self.width - total_board_width) // 2  # Centrage horizontal
        self.offset_y = (self.height - total_board_height) // 2  # Centrage vertical

        # État du jeu
        self.board = [[(0, (0, 0, 0)) for _ in range(self.board_width)] for _ in range(self.board_height)]  # (occupé, couleur)
        self.current_piece = None
        self.current_x = 0
        self.current_y = 0
        self.current_rotation = 0
        self.current_color = (255, 255, 255)

        # Timing pour la gravité
        self.last_fall = time.time()
        self.fall_speed = 0.8  # secondes entre descentes automatiques

        # Statistiques détaillées
        self.pieces_placed = 0
        self.lines_per_level = 10

        # Frame actuelle
        self.current_frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Chiffres pour l'affichage des scores (même style que Pong)
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

        # Initialisation
        self.spawn_piece()

    def start_game(self):
        """Démarre le jeu."""
        self.running = True
        self.paused = False
        self.game_over = False
        print("INFO: Tetris game started")
        # Dessiner la frame initiale pour afficher le score
        self._draw_frame()

    def stop_game(self):
        """Arrête le jeu."""
        self.running = False
        print("INFO: Tetris game stopped")

    def update(self):
        """
        Met à jour l'état du jeu avec la logique complète du Tetris.
        """
        if self.game_over or self.paused or not self.running:
            # Même en pause ou game over, redessiner pour afficher le score
            self._draw_frame()
            return

        # Gestion des contrôles clavier
        self._handle_input()

        # Gravité automatique
        current_time = time.time()
        if current_time - self.last_fall > self.fall_speed:
            if not self.move(0, 1):  # Essayer de descendre
                self._place_piece()  # Placer la pièce si elle ne peut pas descendre
                self._clear_lines()  # Vérifier les lignes complètes
                self.spawn_piece()  # Générer une nouvelle pièce
            self.last_fall = current_time

        # Redessiner la frame
        self._draw_frame()

    def get_frame(self) -> np.ndarray:
        """Retourne la frame actuelle du jeu pour l'affichage."""
        return self.current_frame.copy()

    def _handle_input(self):
        """Gère les entrées clavier accumulées."""
        # Mouvement gauche
        if 'left' in self.keys_pressed or 'q' in self.keys_pressed:
            self.move(-1, 0)
            self.keys_pressed.discard('left')
            self.keys_pressed.discard('q')

        # Mouvement droite
        if 'right' in self.keys_pressed or 'd' in self.keys_pressed:
            self.move(1, 0)
            self.keys_pressed.discard('right')
            self.keys_pressed.discard('d')

        # Rotation
        if 'up' in self.keys_pressed or 'z' in self.keys_pressed:
            self.rotate()
            self.keys_pressed.discard('up')
            self.keys_pressed.discard('z')

        # Descente rapide
        if 'down' in self.keys_pressed or 's' in self.keys_pressed:
            self.move(0, 1)
            self.keys_pressed.discard('down')
            self.keys_pressed.discard('s')

    def move(self, dx, dy):
        """
        Déplace la pièce courante de (dx, dy).
        Retourne True si le mouvement est possible, False sinon.
        """
        new_x = self.current_x + dx
        new_y = self.current_y + dy

        if self._is_valid_position(self.current_piece, new_x, new_y, self.current_rotation):
            self.current_x = new_x
            self.current_y = new_y
            return True
        return False

    def rotate(self):
        """Fait tourner la pièce courante."""
        new_rotation = (self.current_rotation + 1) % len(self.current_piece)
        if self._is_valid_position(self.current_piece, self.current_x, self.current_y, new_rotation):
            self.current_rotation = new_rotation

    def _is_valid_position(self, piece, x, y, rotation):
        """Vérifie si une position est valide (pas de collision)."""
        shape = piece[rotation]
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    # Vérifier les limites du plateau
                    if (x + j < 0 or x + j >= self.board_width or
                        y + i < 0 or y + i >= self.board_height):
                        return False
                    # Vérifier les collisions avec les pièces placées
                    occupied, _ = self.board[y + i][x + j]
                    if occupied:
                        return False
        return True

    def _place_piece(self):
        """Place la pièce courante sur le plateau."""
        shape = self.current_piece[self.current_rotation]
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    self.board[self.current_y + i][self.current_x + j] = (1, self.current_color)

        self.pieces_placed += 1
        self.score += 10  # Points pour avoir placé une pièce

        # Mettre à jour le meilleur score
        if self.score > self.high_score:
            self.high_score = self.score
        
        # Forcer le redessinage
        self._draw_frame()

    def _clear_lines(self):
        """Vérifie et efface les lignes complètes."""
        lines_to_clear = []
        for i, row in enumerate(self.board):
            # Vérifier si tous les éléments de la ligne sont occupés
            if all(occupied for occupied, _ in row):
                lines_to_clear.append(i)

        # Effacer les lignes et faire descendre les autres
        for line in reversed(lines_to_clear):
            del self.board[line]
            self.board.insert(0, [(0, (0, 0, 0)) for _ in range(self.board_width)])

        # Calculer les points
        if lines_to_clear:
            lines_count = len(lines_to_clear)
            self.lines_cleared += lines_count

            # Système de points Tetris classique
            if lines_count == 1:
                self.score += 100 * self.level
            elif lines_count == 2:
                self.score += 300 * self.level
            elif lines_count == 3:
                self.score += 500 * self.level
            elif lines_count == 4:
                self.score += 800 * self.level  # Tetris !

            # Monter de niveau
            if self.lines_cleared >= self.level * self.lines_per_level:
                self.level += 1
                self.fall_speed = max(0.1, self.fall_speed - 0.05)  # Accélérer
            
            # Forcer le redessinage
            self._draw_frame()

    def spawn_piece(self):
        """Génère une nouvelle pièce Tetris."""
        # Choisir une pièce aléatoirement
        piece_index = random.randint(0, len(self.SHAPES) - 1)
        self.current_piece = self.SHAPES[piece_index]
        self.current_color = self.COLORS[piece_index]

        # Position de départ (en haut au centre)
        # Calculer la largeur de la pièce dans sa rotation initiale
        initial_shape = self.current_piece[0]
        piece_width = len(initial_shape[0]) if initial_shape else 0
        self.current_x = self.board_width // 2 - piece_width // 2
        self.current_y = 0
        self.current_rotation = 0

        # Vérifier si la pièce peut être placée (Game Over sinon)
        if not self._is_valid_position(self.current_piece, self.current_x, self.current_y, self.current_rotation):
            self.game_over = True
            print(f"GAME OVER - Score: {self.score}, Lignes: {self.lines_cleared}")
            print(f"High Score: {self.high_score}, Level: {self.level}")

    def _draw_frame(self):
        """Dessine la frame complète du jeu Tetris."""
        # Effacer la frame
        self.current_frame.fill(0)

        # Couleur de fond pour le plateau
        board_bg_color = (20, 20, 20)  # Gris foncé

        # Dessiner le plateau de jeu
        for y in range(self.board_height):
            for x in range(self.board_width):
                occupied, color = self.board[y][x]
                if occupied:  # Cellule occupée
                    self._draw_cell(x, y, color)  # Utiliser la couleur stockée de la pièce
                else:  # Cellule vide
                    self._draw_cell(x, y, board_bg_color)

        # Dessiner la pièce courante
        if self.current_piece and not self.game_over:
            shape = self.current_piece[self.current_rotation]
            for i, row in enumerate(shape):
                for j, cell in enumerate(row):
                    if cell:
                        self._draw_cell(self.current_x + j, self.current_y + i, self.current_color)

        # Dessiner les bordures du plateau
        self._draw_border()

        # Si game over, afficher le message
        if self.game_over:
            self._draw_game_over()

    def _draw_cell(self, board_x, board_y, color):
        """Dessine une cellule du plateau aux coordonnées LED."""
        led_x = self.offset_x + board_x * self.cell_size
        led_y = self.offset_y + board_y * self.cell_size

        for dy in range(self.cell_size):
            for dx in range(self.cell_size):
                if (led_x + dx < self.width and led_y + dy < self.height):
                    self.current_frame[led_y + dy, led_x + dx] = color

    def _draw_border(self):
        """Dessine les bordures du plateau de jeu."""
        border_color = (255, 0, 0)  # Rouge vif

        # Bordure gauche
        for y in range(self.board_height * self.cell_size):
            led_y = self.offset_y + y
            if led_y < self.height:
                self.current_frame[led_y, self.offset_x - 1] = border_color

        # Bordure droite
        for y in range(self.board_height * self.cell_size):
            led_y = self.offset_y + y
            if led_y < self.height:
                self.current_frame[led_y, self.offset_x + self.board_width * self.cell_size] = border_color

        # Bordure basse
        for x in range(self.board_width * self.cell_size + 2):
            led_x = self.offset_x - 1 + x
            if led_x < self.width:
                self.current_frame[self.offset_y + self.board_height * self.cell_size, led_x] = border_color

    def _draw_digit(self, digit: int, x: int, y: int, color: Tuple[int, int, int]):
        """Dessine un chiffre (exactement comme Pong)"""
        pattern = self.DIGITS.get(str(digit), self.DIGITS["0"])
        for row in range(5):
            for col in range(3):
                if pattern[row][col] == "1":
                    px = x + col
                    py = y + row
                    if 0 <= px < self.width and 0 <= py < self.height:
                        self.current_frame[py, px] = color

    def _draw_game_over(self):
        """Dessine l'écran Game Over."""
        # Fond semi-transparent
        overlay = self.current_frame.astype(np.float32)
        overlay *= 0.3
        self.current_frame = overlay.astype(np.uint8)

        # Texte "GAME OVER" centré
        center_x = self.width // 2
        center_y = self.height // 2

        # G (lettre)
        self._draw_letter_pixelated("GAME OVER", center_x - 40, center_y - 10, (255, 255, 0))

        # Score final
        score_text = f"SCORE: {self.score}"
        self._draw_letter_pixelated(score_text, center_x - 30, center_y + 10, (255, 255, 255))

    def _draw_letter_pixelated(self, text, start_x, start_y, color):
        """Dessine du texte pixelisé pour l'écran Game Over."""
        # Définition simple de quelques lettres (3x5 pixels)
        letters = {
            'G': [[1,1,1,1,1], [1,0,0,0,0], [1,0,1,1,0], [1,0,0,0,1], [1,1,1,1,1]],
            'A': [[0,1,1,1,0], [1,0,0,0,1], [1,1,1,1,1], [1,0,0,0,1], [1,0,0,0,1]],
            'M': [[1,0,0,0,1], [1,1,0,1,1], [1,0,1,0,1], [1,0,0,0,1], [1,0,0,0,1]],
            'E': [[1,1,1,1,1], [1,0,0,0,0], [1,1,1,0,0], [1,0,0,0,0], [1,1,1,1,1]],
            'O': [[0,1,1,1,0], [1,0,0,0,1], [1,0,0,0,1], [1,0,0,0,1], [0,1,1,1,0]],
            'V': [[1,0,0,0,1], [1,0,0,0,1], [0,1,0,1,0], [0,1,0,1,0], [0,0,1,0,0]],
            'R': [[1,1,1,0,0], [1,0,0,1,0], [1,1,1,0,0], [1,0,1,0,0], [1,0,0,1,0]],
            'S': [[0,1,1,1,0], [1,0,0,0,0], [0,1,1,1,0], [0,0,0,0,1], [1,1,1,1,0]],
            'C': [[0,1,1,1,0], [1,0,0,0,0], [1,0,0,0,0], [1,0,0,0,0], [0,1,1,1,0]],
            ' ': [[0,0,0,0,0], [0,0,0,0,0], [0,0,0,0,0], [0,0,0,0,0], [0,0,0,0,0]],
            '0': [[0,1,1,1,0], [1,0,0,0,1], [1,0,1,0,1], [1,0,0,0,1], [0,1,1,1,0]],
            '1': [[0,0,1,0,0], [0,1,1,0,0], [0,0,1,0,0], [0,0,1,0,0], [0,1,1,1,0]],
            '2': [[0,1,1,1,0], [0,0,0,0,1], [0,1,1,1,0], [1,0,0,0,0], [1,1,1,1,1]],
            '3': [[0,1,1,1,0], [0,0,0,0,1], [0,0,1,1,0], [0,0,0,0,1], [0,1,1,1,0]],
            '4': [[1,0,0,0,1], [1,0,0,0,1], [1,1,1,1,1], [0,0,0,0,1], [0,0,0,0,1]],
            '5': [[1,1,1,1,1], [1,0,0,0,0], [1,1,1,1,0], [0,0,0,0,1], [1,1,1,1,0]],
            '6': [[0,1,1,1,0], [1,0,0,0,0], [1,1,1,1,0], [1,0,0,0,1], [0,1,1,1,0]],
            '7': [[1,1,1,1,1], [0,0,0,0,1], [0,0,0,1,0], [0,0,1,0,0], [0,1,0,0,0]],
            '8': [[0,1,1,1,0], [1,0,0,0,1], [0,1,1,1,0], [1,0,0,0,1], [0,1,1,1,0]],
            '9': [[0,1,1,1,0], [1,0,0,0,1], [0,1,1,1,1], [0,0,0,0,1], [0,1,1,1,0]],
            ':': [[0,0,0,0,0], [0,0,1,0,0], [0,0,0,0,0], [0,0,1,0,0], [0,0,0,0,0]]
        }

        x_pos = start_x
        for char in text:
            if char in letters:
                pattern = letters[char]
                for y, row in enumerate(pattern):
                    for x, pixel in enumerate(row):
                        if pixel:
                            led_x = x_pos + x
                            led_y = start_y + y
                            if (0 <= led_x < self.width and 0 <= led_y < self.height):
                                self.current_frame[led_y, led_x] = color
                x_pos += 6  # Espacement entre lettres



    def set_key_pressed(self, key: str, pressed: bool):
        """
        Gère les entrées clavier.
        La logique de mouvement (gauche, droite, rotation) doit être implémentée ici.
        """
        if pressed:
            self.keys_pressed.add(key)
            print(f"DEBUG: Key '{key}' pressed")
            # --- GESTION DES CONTRÔLES À IMPLÉMENTER ---
            # Exemple:
            # if key in ['q', 'left']: # Gauche
            # elif key in ['d', 'right']: # Droite
            # elif key in ['s', 'down']: # Descente
            # elif key in ['z', 'up']: # Rotation
        else:
            self.keys_pressed.discard(key)

    def pause_game(self):
        """Met le jeu en pause."""
        if self.running and not self.game_over:
            self.paused = True
            print("INFO: Tetris game paused")

    def resume_game(self):
        """Reprend le jeu."""
        if self.running and not self.game_over:
            self.paused = False
            print("INFO: Tetris game resumed")

    def restart(self):
        """Redémarre le jeu."""
        print("INFO: Tetris game restarting")
        self.reset_game()
        self.start_game()
        
    def reset_game(self):
        """Réinitialise l'état du jeu."""
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.paused = False
        self.pieces_placed = 0
        self.fall_speed = 0.8
        self.last_fall = time.time()

        # Réinitialiser le plateau
        self.board = [[(0, (0, 0, 0)) for _ in range(self.board_width)] for _ in range(self.board_height)]

        # Générer une nouvelle pièce
        self.spawn_piece()
        
        # Dessiner la frame initiale pour afficher le score
        self._draw_frame()

    def get_game_stats(self) -> dict:
        """Retourne les statistiques du jeu."""
        return {
            "score": self.score,
            "high_score": self.high_score,
            "level": self.level,
            "lines_cleared": self.lines_cleared
        }

    def is_game_over(self) -> bool:
        """Vérifie si le jeu est terminé."""
        return self.game_over

    def is_paused(self) -> bool:
        """Vérifie si le jeu est en pause."""
        return self.paused
        
    def is_running(self) -> bool:
        """Vérifie si le jeu a été démarré et pas arrêté (même en Game Over)."""
        return self.running

    def is_actively_playing(self) -> bool:
        """Vérifie si le jeu est en cours ET pas en game over."""
        return self.running and not self.game_over