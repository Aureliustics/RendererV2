import ctypes
import sys
from sdl2 import *
import sdl2.ext

# rules for codebase: use SCREAMING_SNAKE_CASE for constants
# https://lukems.github.io/py-sdl2/modules/index.html for docs

WINDOW_SIZE = 400

# init the window
SDL_Init(SDL_INIT_VIDEO)
window = SDL_CreateWindow(
    b"Renderer V2",
    SDL_WINDOWPOS_CENTERED,
    SDL_WINDOWPOS_CENTERED,
    WINDOW_SIZE, WINDOW_SIZE,
    SDL_WINDOW_SHOWN
)
renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_SOFTWARE)

running = True
while running:
    event = SDL_Event()
    while SDL_PollEvent(ctypes.byref(event)):
        if event.type == SDL_QUIT:
            running = False
    # not great looking but i am still figuring out key inputs
    keys = SDL_GetKeyboardState(None)
    if keys[SDL_SCANCODE_W]:
        print("W")
    if keys[SDL_SCANCODE_S]:
        print("S")
    if keys[SDL_SCANCODE_A]:
        print("A")
    if keys[SDL_SCANCODE_D]:
        print("D")
    if keys[SDL_SCANCODE_SPACE]:
        print("Space")
    if keys[SDL_SCANCODE_LCTRL]:
        print("Ctrl")

SDL_Quit()
