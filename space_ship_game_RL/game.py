# 太空生存戰
import pygame
import random 
import os
from setting import *

# 遊戲初始化 and 創建視窗
# pygame.init()
# pygame.mixer.init()
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_mode((WIDTH, HEIGHT))

from power import Power
from explosion import Explosion
from rock import Rock
from player import Player
import numpy as np

ALERT_FRAME_MARGIN = 45

# 載入圖片
BASE_PATH = os.path.dirname(__file__)
background_img = pygame.image.load(os.path.join(BASE_PATH, "img", "background.png"))

font_name = os.path.join(BASE_PATH, "font.ttf")

class Game:
    def __init__(self, debug=False):
        self.debug = debug
        self.running = True
        self.player = pygame.sprite.GroupSingle()
        self.player.add(Player())
        self.all_sprites = pygame.sprite.Group()
        self.rocks = pygame.sprite.Group()
        for i in range(8):
            self.new_rock()
        self.powers = pygame.sprite.Group()

        self.score = 0
        self.surface = pygame.Surface((WIDTH, HEIGHT))  # 用來 off-screen 畫畫的
        self.state = pygame.surfarray.array3d(self.surface).astype(np.uint8).swapaxes(0, 1) # shape (500, 600, 3)
        self.action = 0

        self.is_collided = False
        self.is_hit_rock = False
        self.is_power = False

             
    def draw_text(self, surf, text, size, x, y):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.centerx = x
        text_rect.top = y
        surf.blit(text_surface, text_rect)

    def draw_health(self, surf, hp, x, y):
        if hp < 0:
            hp = 0
        BAR_LENGTH = 100
        BAR_HEIGHT = 10
        fill = (hp/100)*BAR_LENGTH
        outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
        fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
        pygame.draw.rect(surf, GREEN, fill_rect)
        pygame.draw.rect(surf, WHITE, outline_rect, 2)

                
    def new_rock(self):
        r = Rock()
        self.all_sprites.add(r)
        self.rocks.add(r)

    def collide_bullet_rock(self):
        # 判斷子彈 石頭相撞
        hits = pygame.sprite.groupcollide(self.rocks, self.player.sprite.bullet_group, True, True)
        if hits:
            for hit in hits:
                # random.choice(expl_sounds).play()
                self.score += hit.radius * 2
                expl = Explosion(hit.rect.center, 'lg')
                self.all_sprites.add(expl)
                if random.random() > 0.8:
                    pow = Power(hit.rect.center)
                    self.all_sprites.add(pow)
                    self.powers.add(pow)
                self.new_rock()
            
            self.is_hit_rock = True

        else:
            self.is_hit_rock = False

    def collide_player_rock(self):
        # 判斷飛船 石頭相撞
        hits = pygame.sprite.spritecollide(self.player.sprite, self.rocks, True, pygame.sprite.collide_circle)
        if hits:
            self.player.sprite.health -= hits[0].radius * 1
            expl = Explosion(hits[0].rect.center, 'sm')
            self.all_sprites.add(expl)
            self.new_rock()
            self.is_collided = True
        else:
            self.is_collided = False

    def collide_player_power(self):
        # 判斷飛船 寶物相撞
        hits = pygame.sprite.spritecollide(self.player.sprite, self.powers, True)
        if hits:
            for hit in hits:
                if hit.type == 'shield':
                    self.player.sprite.health += 20
                    if self.player.sprite.health > 100:
                        self.player.sprite.health = 100
                elif hit.type == 'gun':
                    self.player.sprite.gunup()
            self.is_power = True
        else:
            self.is_power = False

    def check_state(self):
        if self.player.sprite.health <= 0:
            death_expl = Explosion(self.player.sprite.rect.center, 'player')
            self.all_sprites.add(death_expl)
            
            self.player.sprite.lives -= 1
            # self.player.sprite.health = 100
            self.player.sprite.hide()

        if self.player.sprite.lives == 0:
            # die_sound.play()
            self.running = False

    def update(self, action):
        # 更新遊戲
        self.all_sprites.update()
        self.player.update(action)
        self.collide_bullet_rock()
        self.collide_player_rock()
        self.collide_player_power()
        self.check_state()

    def draw(self, screen=None):
        surface = self.surface if screen is None else screen
        surface.fill(BLACK)
        surface.blit(background_img, (0, 0))
        self.all_sprites.draw(surface)
        self.player.draw(surface)
        self.player.sprite.bullet_group.draw(surface)
        self.draw_text(surface, str(self.score), 18, WIDTH/2, 10)
        self.draw_health(surface, self.player.sprite.health, 5, 15)
        if self.debug:
            self.draw_velocity_vectors(surface)
            for rock in self.rocks:
                pygame.draw.rect(surface, (255, 0, 0), rock.rect, 1)
                pygame.draw.line(surface, (0, 255, 0), rock.rect.center, self.player.sprite.rect.center)
            pygame.draw.rect(surface, (0, 0, 255), self.player.sprite.rect, 1)
                        
            zone_width = WIDTH // 8
            zone_color = (255, 0, 0)
            fill_color = (255, 0, 0, 100)  # RGBA for semi-transparency
        
            # Create a transparent surface for filling
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
            for i in range(8):
                x_start = i * zone_width
                zone_height = self.player.sprite.rect.height
                zone_y = self.player.sprite.rect.bottom - zone_height
                zone_rect = pygame.Rect(x_start, zone_y, zone_width, zone_height)
            
                for rock in self.rocks:
                    player_y = self.player.sprite.rect.bottom
                    frames_until_impact = (player_y - rock.rect.top) / max(rock.speedy, 1)
            
                    # Predict where the rock will be horizontally at impact time
                    predicted_x = rock.rect.centerx + rock.speedx * frames_until_impact
                    predicted_left = predicted_x - rock.rect.width // 2
                    predicted_right = predicted_x + rock.rect.width // 2
            
                    zone_left = x_start
                    zone_right = x_start + zone_width
            
                    # Will the rock pass through this zone at impact?
                    if predicted_right > zone_left and predicted_left < zone_right:
                        # Check if there's still time to escape
                        player_x = self.player.sprite.rect.centerx
                        dist_to_left = abs(player_x - zone_left)
                        dist_to_right = abs(player_x - zone_right)
                        dist_to_exit = min(dist_to_left, dist_to_right)
            
                        player_speed = max(abs(self.player.sprite.speedx), 1)
                        time_to_escape = dist_to_exit / player_speed
                        
                        if frames_until_impact < time_to_escape + ALERT_FRAME_MARGIN:
                            pygame.draw.rect(overlay, fill_color, zone_rect)
                            break
                pygame.draw.rect(surface, zone_color, zone_rect, 1)
            
            surface.blit(overlay, (0, 0))

        # 更新 state
        self.state = pygame.surfarray.array3d(surface).astype(np.uint8).swapaxes(0, 1)

        # 只有 render 模式才更新視窗
        if screen is not None:
            pygame.display.update()

    def draw_velocity_vectors(self, surface):
        # Draw velocity vectors for rocks
        for rock in self.rocks:
            start = (rock.rect.centerx, rock.rect.centery)
            end = (start[0] + rock.speedx * 5, start[1] + rock.speedy * 5)
            pygame.draw.line(surface, (255, 0, 0), start, end, 2)  # Red line for rock velocity
    
        # Draw velocity vector for player if velocity info is available
        player = self.player.sprite
        if hasattr(player, 'speedx'):
            start = (player.rect.centerx, player.rect.centery)
            end = (start[0] + player.speedx * 5, start[1])  # Player only moves left-right
            pygame.draw.line(surface, (0, 255, 0), start, end, 2)  # Green line for player
    
    def get_zone_danger_state(self, lookahead_frames=60, alert_margin=45):
        zone_width = WIDTH // 8
        player_y = self.player.sprite.rect.bottom
        player_x = self.player.sprite.rect.centerx
        player_speed = max(abs(self.player.sprite.speedx), 1)
        zone_threat = [0.0] * 8
    
        for rock in self.rocks:
            frames_to_impact = (player_y - rock.rect.top) / max(rock.speedy, 1)
            if 0 < frames_to_impact <= lookahead_frames:
                predicted_x = rock.rect.centerx + rock.speedx * frames_to_impact
                predicted_left = predicted_x - rock.rect.width // 2
                predicted_right = predicted_x + rock.rect.width // 2
    
                for i in range(8):
                    zone_left = i * zone_width
                    zone_right = zone_left + zone_width
    
                    if predicted_right > zone_left and predicted_left < zone_right:
                        dist_to_left = abs(player_x - zone_left)
                        dist_to_right = abs(player_x - zone_right)
                        dist_to_exit = min(dist_to_left, dist_to_right)
    
                        time_to_escape = dist_to_exit / player_speed
    
                        if frames_to_impact < time_to_escape + alert_margin:
                            zone_threat[i] = 1.0
    
        return zone_threat


    def get_extended_state(self):
        """
        Return a dict of processed state features (used in RL).
        """
        zone_danger = self.get_zone_danger_state()
        player_x = self.player.sprite.rect.centerx / WIDTH
        player_speed = self.player.sprite.speedx / 10  # normalize
        health = self.player.sprite.health / 100
    
        return {
            "zone_danger": np.array(zone_danger, dtype=np.float32),
            "player_x": player_x,
            "player_speed": player_speed,
            "health": health,
        }

    def get_state_info(self):
        """Extracts useful game info for reward shaping."""
        player_x = self.player.sprite.rect.centerx
        player_y = self.player.sprite.rect.centery
        player_speed = self.player.sprite.speedx
        danger_zones = []
    
        # Use same predictive logic as the debug zone alert
        zone_width = WIDTH // 8
        frames_ahead = 15  # tweak for "how early to predict"
        
        for i in range(8):
            x_start = i * zone_width
            x_end = x_start + zone_width
    
            for rock in self.rocks:
                future_y = rock.rect.top + rock.speedy * frames_ahead
                future_x = rock.rect.centerx + rock.speedx * frames_ahead
                left = future_x - rock.rect.width // 2
                right = future_x + rock.rect.width // 2
    
                if right > x_start and left < x_end:
                    danger_zones.append(i)
                    break
    
        # Count how many rocks are near (within vertical distance)
        danger_count = sum(1 for rock in self.rocks if abs(rock.rect.centery - player_y) < 120)
    
        return {
            "player_x": player_x,
            "player_speed": player_speed,
            "danger_zones": danger_zones,
            "zone_id": player_x // zone_width,
            "danger_count": danger_count,
        }


