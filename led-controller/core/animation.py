import numpy as np
import time
import threading
import random

class AnimationEngine:
    """Génère et gère les animations pour la grille de LEDs."""
    
    def __init__(self, width=128, height=128):
        self.width = width
        self.height = height
        self.animations = {
            "Couleur Solide": self.solid_color,
            "Vague Arc-en-ciel": self.rainbow_wave,
            "Plasma": self.plasma,
            "Pluie de Météorites": self.meteor_shower,
            "Vagues de Couleur": self.color_waves,
            "Sphère 3D Tournante": self.sphere_3d,
            "Tunnel Optique": self.optical_tunnel,
            "Damier Mouvant": self.moving_checkerboard,
        }
        self.current_animation = None
        self.running = False
        self.thread = None
        self.frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.start_time = time.time()
        
        # Paramètres spécifiques aux animations
        self.animation_parameters = {
            "color": (255, 0, 0),
            "meteors": []
        }

    def get_frame(self):
        """Retourne la dernière frame générée."""
        return self.frame

    def play(self, animation_name: str, **kwargs):
        """Démarre une animation."""
        if animation_name not in self.animations:
            raise ValueError(f"Animation '{animation_name}' non trouvée.")
        
        self.stop()
        
        # Réinitialiser les paramètres si nécessaire
        if animation_name == "Pluie de Météorites":
            self.animation_parameters["meteors"] = []
            
        self.current_animation = self.animations[animation_name]
        self.animation_parameters.update(kwargs)
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        """Arrête l'animation en cours."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.5)
        self.current_animation = None

    def _run(self):
        """Boucle de génération des frames."""
        self.start_time = time.time()
        last_frame_time = 0
        while self.running:
            start_render_time = time.perf_counter()
            
            self.frame = self.current_animation()
            
            # Contrôle dynamique des FPS - 45 FPS pour stabilité
            render_duration = time.perf_counter() - start_render_time
            sleep_time = max(0, (1/45.0) - render_duration)
            time.sleep(sleep_time)

    # --- Définitions des animations ---

    def solid_color(self):
        """Affiche une couleur unie."""
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        frame[:, :] = self.animation_parameters.get("color", (255, 0, 0))
        return frame

    def rainbow_wave(self):
        """Génère une vague de couleurs arc-en-ciel (optimisé)."""
        t = (time.time() - self.start_time) * 0.5
        
        x = np.arange(self.width)
        y = np.arange(self.height)
        X, Y = np.meshgrid(x, y)
        
        hue = (X + Y + t * 20) % self.width / self.width
        
        # Conversion HSV vers RGB vectorisée (plus rapide)
        i = (hue * 6.0).astype(int)
        f = (hue * 6.0) - i
        p = 1.0 * (1.0 - 1.0)
        q = 1.0 * (1.0 - f * 1.0)
        t_ = 1.0 * (1.0 - (1.0 - f) * 1.0)
        
        i %= 6
        
        rgb = np.zeros((self.height, self.width, 3))
        
        # Masques pour chaque cas de couleur
        idx0 = i == 0
        idx1 = i == 1
        idx2 = i == 2
        idx3 = i == 3
        idx4 = i == 4
        idx5 = i == 5
        
        # S'assurer que les tableaux ont la même forme avant l'assignation
        rgb[idx0, 0] = 1.0
        rgb[idx0, 1] = t_[idx0]
        rgb[idx0, 2] = p
        
        rgb[idx1, 0] = q[idx1]
        rgb[idx1, 1] = 1.0
        rgb[idx1, 2] = p
        
        rgb[idx2, 0] = p
        rgb[idx2, 1] = 1.0
        rgb[idx2, 2] = t_[idx2]
        
        rgb[idx3, 0] = p
        rgb[idx3, 1] = q[idx3]
        rgb[idx3, 2] = 1.0
        
        rgb[idx4, 0] = t_[idx4]
        rgb[idx4, 1] = p
        rgb[idx4, 2] = 1.0
        
        rgb[idx5, 0] = 1.0
        rgb[idx5, 1] = p
        rgb[idx5, 2] = q[idx5]
        
        return (rgb * 255).astype(np.uint8)

    def plasma(self):
        """Génère un effet de plasma."""
        t = time.time() - self.start_time
        
        x = np.arange(self.width)
        y = np.arange(self.height)
        X, Y = np.meshgrid(x, y)

        v = (np.sin(X / 16.0 + t) +
             np.sin(Y / 8.0 + t) +
             np.sin((X + Y) / 16.0 + t) +
             np.sin(np.sqrt(X**2 + Y**2) / 8.0 + t))
        
        v = (v + 4) / 8.0 # Normaliser entre 0 et 1
        
        r = (np.sin(v * np.pi) * 0.5 + 0.5) * 255
        g = (np.sin(v * np.pi + 2 * np.pi / 3) * 0.5 + 0.5) * 255
        b = (np.sin(v * np.pi + 4 * np.pi / 3) * 0.5 + 0.5) * 255
        
        return np.stack([r, g, b], axis=-1).astype(np.uint8)

    def meteor_shower(self):
        """Simule une pluie de météorites."""
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Estomper l'image précédente
        fade_amount = 0.90
        self.frame = (self.frame * fade_amount).astype(np.uint8)
        
        # Ajouter de nouveaux météores
        if random.random() < 0.3: # Probabilité d'un nouveau météore
            meteor = {
                "x": random.randint(0, self.width - 1),
                "y": 0,
                "len": random.randint(5, 15),
                "speed": random.uniform(1.0, 3.0),
                "color": (random.randint(128, 255), random.randint(128, 255), random.randint(128, 255))
            }
            self.animation_parameters["meteors"].append(meteor)
            
        # Mettre à jour et dessiner les météores
        meteors_to_keep = []
        for meteor in self.animation_parameters["meteors"]:
            meteor["y"] += meteor["speed"]
            
            # Dessiner la traînée
            for i in range(meteor["len"]):
                if 0 <= meteor["y"] - i < self.height and 0 <= meteor["x"] < self.width:
                    intensity = 1.0 - (i / meteor["len"])
                    color = tuple(c * intensity for c in meteor["color"])
                    y = int(meteor["y"] - i)
                    x = int(meteor["x"])
                    self.frame[y, x] = color
            
            if meteor["y"] - meteor["len"] < self.height:
                meteors_to_keep.append(meteor)
                
        self.animation_parameters["meteors"] = meteors_to_keep
        
        return self.frame
        
    def color_waves(self):
        """Génère des vagues de couleur."""
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        t = time.time() - self.start_time
        
        x = np.arange(self.width)
        y = np.arange(self.height)
        X, Y = np.meshgrid(x, y)
        
        # Ondes basées sur la distance au centre
        center_x, center_y = self.width / 2, self.height / 2
        dist = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
        
        wave = np.sin(dist / 8.0 - t * 2.0)
        
        # Normaliser entre 0 et 1
        wave = (wave + 1) / 2.0
        
        # Appliquer à une couleur
        base_color = np.array([0, 100, 255])
        frame[:, :] = base_color * wave[:, :, np.newaxis]
        
        return frame.astype(np.uint8) 

    def sphere_3d(self):
        """Affiche une sphère 3D qui tourne sur elle-même (optimisé avec NumPy)."""
        t = (time.time() - self.start_time) * 0.7
        cx, cy = self.width // 2, self.height // 2
        radius = min(self.width, self.height) // 2 - 4
        
        # Créer les grilles de coordonnées
        x = np.arange(self.width)
        y = np.arange(self.height)
        X, Y = np.meshgrid(x, y)
        
        # Coordonnées normalisées
        nx = (X - cx) / radius
        ny = (Y - cy) / radius
        
        # Masque pour la sphère
        sphere_mask = nx**2 + ny**2 <= 1.0
        
        # Calcul de la profondeur (z) vectorisé
        nz = np.sqrt(1.0 - nx**2 - ny**2)
        nz = np.where(sphere_mask, nz, 0)
        
        # Rotation autour de l'axe Y (vectorisé)
        angle = t
        rx = np.cos(angle) * nx + np.sin(angle) * nz
        rz = -np.sin(angle) * nx + np.cos(angle) * nz
        
        # Calcul de la lumière vectorisé
        light_dir = np.array([0.5, -1, 1])
        light_dir = light_dir / np.linalg.norm(light_dir)
        
        # Normalisation vectorisée
        norm_length = np.sqrt(rx**2 + ny**2 + rz**2)
        norm_length = np.where(norm_length > 0, norm_length, 1)
        
        nx_norm = rx / norm_length
        ny_norm = ny / norm_length
        nz_norm = rz / norm_length
        
        # Produit scalaire vectorisé
        intensity = nx_norm * light_dir[0] + ny_norm * light_dir[1] + nz_norm * light_dir[2]
        intensity = np.maximum(0.0, intensity)
        
        # Couleur de la sphère
        base_color = np.array([80, 180, 255])
        color = (base_color * (0.3 + 0.7 * intensity)).astype(np.uint8)
        
        # Appliquer le masque
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        frame[sphere_mask] = color[sphere_mask]
        
        return frame

    def optical_tunnel(self):
        """Effet tunnel illusion d'optique (spirale mouvante, optimisé)."""
        t = (time.time() - self.start_time) * 1.2
        cx, cy = self.width // 2, self.height // 2
        
        # Créer les grilles de coordonnées
        x = np.arange(self.width)
        y = np.arange(self.height)
        X, Y = np.meshgrid(x, y)
        
        # Calculs vectorisés
        dx = X - cx
        dy = Y - cy
        r = np.sqrt(dx*dx + dy*dy) + 1e-5
        angle = np.arctan2(dy, dx)
        
        # Effet tunnel vectorisé
        val = 0.5 + 0.5 * np.sin(8*angle + t - r/8 + 2*np.sin(t/2))
        c = (255 * val).astype(np.uint8)
        
        frame = np.stack([c, c, c], axis=-1)
        return frame

    def moving_checkerboard(self):
        """Damier mouvant (illusion d'optique, optimisé)."""
        t = (time.time() - self.start_time) * 0.8
        freq = 8
        
        # Créer les grilles de coordonnées
        x = np.arange(self.width)
        y = np.arange(self.height)
        X, Y = np.meshgrid(x, y)
        
        # Calculs vectorisés pour le mouvement
        x_offset = (8 * np.sin(t + Y/10)).astype(int)
        y_offset = (8 * np.cos(t + X/10)).astype(int)
        
        # Damier vectorisé
        val = ((X + x_offset) // freq + (Y + y_offset) // freq) % 2
        c = np.where(val == 0, 255, 30).astype(np.uint8)
        
        frame = np.stack([c, c, c], axis=-1)
        return frame 