import ctypes
import sys
from sdl2 import *
import sdl2.ext

# rules for codebase: use SCREAMING_SNAKE_CASE for constants
# https://lukems.github.io/py-sdl2/modules/index.html for docs

WINDOW_SIZE = 400
WIDTH = WINDOW_SIZE
HEIGHT = WINDOW_SIZE

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
texture = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_ARGB8888,
                            SDL_TEXTUREACCESS_STREAMING, WIDTH, HEIGHT)

# init frame buffer
framebuffer = (ctypes.c_uint32 * (WIDTH * HEIGHT))() # ctypes.c_uint32 since each pixel is a 32 bit int

# fill each pixel with white, could prob make this the clear function later too
for i in range(WIDTH * HEIGHT):
    framebuffer[i] = 0xFFFFFFFF  # white in argb (alpha, red, green, blue)

# displaying the frame buffer onto the screen (do not remove)
SDL_UpdateTexture(texture, None, framebuffer, WIDTH * 4) # copies buffer memory into SDL texture
SDL_RenderClear(renderer) # clear last frame
SDL_RenderCopy(renderer, texture, None, None) # draw the pixels to window
SDL_RenderPresent(renderer) # present the pixels

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
