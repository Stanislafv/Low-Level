import time, random, threading, pygame, base.folders as folders

pygame.mixer.init()

class MusicPlayer():
    @staticmethod
    def start():
        def play():
            time.sleep(random.randint(30, 40))
            while True:
                music_name = random.choice(folders.music.list())
                print(f"Playing: <{folders.music.path(music_name)}>")
                pygame.mixer.music.load(folders.music.path(music_name))
                pygame.mixer.music.set_volume(folders.folder.config.get("music_volume", 0.5))
                pygame.mixer.music.play(0)
                while pygame.mixer.music.get_busy():
                    pygame.mixer.music.set_volume(folders.folder.config.get("music_volume", 0.5))
                    time.sleep(0.1)
                time.sleep(random.randint(40, 60))

        thread = threading.Thread(target=play, daemon=True)
        thread.start()
        return thread

    @staticmethod
    def play(path, volume=0.7):
        sound = pygame.mixer.Sound(folders.sounds.path(f"{path}.ogg"))
        sound.set_volume(volume*folders.folder.config.get("volume", 1))
        sound.play()
        return sound