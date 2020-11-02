from pathlib import Path
import moviepy.video.io.ImageSequenceClip
import random

IMG_FOLDER = Path("/home/keddad/Documents/dataset")
OUT_FOLDER = Path("/home/keddad/")

N_VIDS = 5
N_IMAGES = 20
FPS = 5

possible_images = [str(f) for f in IMG_FOLDER.rglob("**/*.jpg")]

for i in range(N_VIDS):
    moviepy.video.io.ImageSequenceClip.ImageSequenceClip(random.choices(possible_images, k=N_IMAGES), fps=FPS).write_videofile(str(OUT_FOLDER) + f"/video_{i}.mp4")