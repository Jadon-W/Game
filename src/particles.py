# particle.py

import pygame
import random
import config


class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, particle_type):
        super().__init__()
        self.particle_type = particle_type
        self.image = pygame.Surface((5, 5), pygame.SRCALPHA)
        if particle_type == 'leaf':
            self.image.fill(config.YELLOW)  # Simple representation
        elif particle_type == 'snowflake':
            self.image.fill(config.WHITE)
        elif particle_type == 'firefly':
            pygame.draw.circle(self.image, config.YELLOW, (2, 2), 2)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = random.uniform(1, 3)
        self.direction = random.uniform(-0.5, 0.5)
        self.twinkle = random.randint(0, 60)
    
    def update(self):
        self.rect.x += self.direction
        self.rect.y += self.speed
        self.twinkle -= 1
        if self.twinkle <= 0:
            # Toggle visibility for twinkling effect
            self.image.set_alpha(random.choice([150, 255]))
            self.twinkle = random.randint(30, 60)
        if self.rect.y > config.HEIGHT:
            self.kill()

class ParticleSystem:
    def __init__(self, time_manager):
        self.time_manager = time_manager
        self.particles = pygame.sprite.Group()
        self.spawn_timer = 0
        self.max_particles = 100  # Maximum active particles
    
    def update(self):
        season = self.time_manager.get_current_season()
        phase = self.time_manager.get_time_of_day()
        
        # Determine particle type based on season
        particle_type = None
        if season == 'Autumn':
            particle_type = 'leaf'
        elif season == 'Winter':
            particle_type = 'snowflake'
        elif season == 'Summer' and phase == 'night':
            particle_type = 'firefly'
        
        # Spawn particles during certain phases
        if particle_type and (phase in ['day', 'dawn', 'dusk'] or (season == 'Summer' and phase == 'night')):
            self.spawn_timer += 1
            spawn_rate = 10  # Lower spawn rate for fireflies
            if particle_type == 'firefly':
                spawn_rate = 60  # Less frequent
            if self.spawn_timer >= spawn_rate and len(self.particles) < self.max_particles:
                self.spawn_particle(particle_type)
                self.spawn_timer = 0
        
        self.particles.update()
    
    def spawn_particle(self, particle_type):
        """
        Spawn particles with behavior based on type.
        """
        x = random.randint(0, config.WIDTH)
        y = 0  # Spawn at the top for snowflakes and leaves
        if particle_type == 'firefly':
            y = random.randint(0, config.HEIGHT // 2)  # Fireflies appear in lower half
        particle = Particle(x, y, particle_type)
        self.particles.add(particle)
    
    def draw(self, surface, camera):
        for particle in self.particles:
            # Adjust position based on camera
            draw_x = particle.rect.x - camera.offset_x
            draw_y = particle.rect.y - camera.offset_y
            surface.blit(particle.image, (draw_x, draw_y))
