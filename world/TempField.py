import numpy as np
from base.folders import folder, saves
import os

class TempField:
    def __init__(self, sizeY, sizeX, ambient, relax=0.01, diffusion=0.15):
        self.field = np.full((sizeY, sizeX), ambient, dtype=np.float32)

        self.ambient = ambient
        self.relax = relax
        self.diffusion = diffusion

    def load(self, name):
        if not os.path.exists(path:=saves.path(name)):
            folder.log.write(f"Sector <{path}> not exists", type="LoadWarning")
            return

        world = saves.mkdir(name)

        if not os.path.exists(world.path("TempField.npy")):
            folder.log.write(f"TempField.npy in <{path}> not exists", type="LoadWarning")
            return
        
        world = saves.mkdir(name)
        data = np.load(world.path("TempField.npy"))

        if data.dtype != np.float32:
            folder.log.write(f"TempField dtype {data.dtype} != float32", type="LoadWarning")
            data = data.astype(np.float32)

        self.field = data

    def save(self, name):
        world = saves.mkdir(name)
        np.save(world.path("TempField.npy"), self.field)

    def update(self, dt):  
        T = self.field      
        lap = (
            np.roll(T, 1, 0) + np.roll(T, -1, 0) +
            np.roll(T, 1, 1) + np.roll(T, -1, 1)
            - 4 * T)
        
        T += lap * self.diffusion * dt
        T += (self.ambient - T) * self.relax * dt

    def __repr__(self):
        return f"ambient: {self.ambient}, relax: {self.relax}, diffusion: {self.diffusion}"