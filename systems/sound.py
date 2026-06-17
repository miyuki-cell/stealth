import os
import pygame

class SoundManager:
    def __init__(self):
        self.lobby_music = None
        self.gameover_sound = None
        self.win_sound = None
        self.blip_sound = None
        self.music_playing = False
        self._load()

    def _load(self):
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        lobby_path = os.path.join(base, "assets", "lobby.mp3")
        go_path    = os.path.join(base, "assets", "gameover.mp3")
        win_path   = os.path.join(base, "assets", "win.mp3")
        blip_path  = os.path.join(base, "assets", "Blip.wav")

        if os.path.exists(go_path):
            try:
                self.gameover_sound = pygame.mixer.Sound(go_path)
                self.gameover_sound.set_volume(0.8)
            except Exception:
                pass

        if os.path.exists(blip_path):
            try:
                self.blip_sound = pygame.mixer.Sound(blip_path)
                self.blip_sound.set_volume(0.5)
            except Exception:
                pass

        if os.path.exists(win_path):
            try:
                self.win_sound = pygame.mixer.Sound(win_path)
                self.win_sound.set_volume(0.6)
            except Exception:
                pass

        self._lobby_path = lobby_path if os.path.exists(lobby_path) else None
        self._go_path    = go_path    if os.path.exists(go_path)    else None

    def play_blip(self):
        if self.blip_sound:
            try:
                self.blip_sound.play()
            except Exception:
                pass

    def play_lobby(self):
        if self._lobby_path and not self.music_playing:
            try:
                pygame.mixer.music.load(self._lobby_path)
                pygame.mixer.music.set_volume(0.45)
                pygame.mixer.music.play(-1)
                self.music_playing = True
            except Exception:
                pass

    def stop_lobby(self):
        if self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False

    def play_gameover(self):
        self.stop_lobby()
        if self.gameover_sound:
            try:
                self.gameover_sound.play()
            except Exception:
                pass

    def stop_gameover(self):
        if self.gameover_sound:
            try:
                self.gameover_sound.stop()
            except Exception:
                pass

    def play_win(self):
        if self.win_sound:
            try:
                self.win_sound.play()
            except Exception:
                pass

    def stop_win(self):
        if self.win_sound:
            try:
                self.win_sound.stop()
            except Exception:
                pass

    def fade_out(self, ms=800):
        try:
            pygame.mixer.music.fadeout(ms)
            self.music_playing = False
        except Exception:
            pass