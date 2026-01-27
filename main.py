import ctypes
import sys
from sdl2 import *
import sdl2.ext

# rules for codebase: use SCREAMING_SNAKE_CASE for constants
# https://lukems.github.io/py-sdl2/modules/index.html for docs

WINDOW_SIZE = 400
WIDTH = WINDOW_SIZE
HEIGHT = WINDOW_SIZE

WHITE = 0xFFFFFFFF
GREEN = 0x05871f
LIGHT_BLUE = 0x23accf


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
    framebuffer[i] = WHITE  # white in argb (alpha, red, green, blue)

# displaying the frame buffer onto the screen (do not remove)
SDL_UpdateTexture(texture, None, framebuffer, WIDTH * 4) # copies buffer memory into SDL texture
SDL_RenderClear(renderer) # clear last frame
SDL_RenderCopy(renderer, texture, None, None) # draw the pixels to window
SDL_RenderPresent(renderer) # present the pixels

def pixel(x, y, colour):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        framebuffer[y * WIDTH + x] = colour

# unfinished
def draw_line(x0, x1, y0, y1, colour): # draw line using point intercept form
    dx = abs(x1 - x0) # dx = delta x (change in x) dy = delta y (change in y)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1 # sx (step x) to step right (1) when x1 better than x0 else step left (-1) 
    sy = 1 if y0 < y1 else -1 # sy (step y) to step up (1) when x1 better than x0 else step down (-1) 
    err = dx - dy

    while True:
        pixel(x0, y0, colour)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy: # if error is large enough to step into x dir
            err -= dy
            x0 += sx
        if e2 < dx: # if error is large enough to step into y dir
            err += dy
            y0 += sy


running = True
while running:
    event = SDL_Event()
    while SDL_PollEvent(ctypes.byref(event)):
        if event.type == SDL_QUIT:
            running = False
    # not great looking but i am still figuring out key inputs
    onkey = SDL_GetKeyboardState(None)
    if onkey[SDL_SCANCODE_W]:
        print("W")
    if onkey[SDL_SCANCODE_S]:
        print("S")
    if onkey[SDL_SCANCODE_A]:
        print("A")
    if onkey[SDL_SCANCODE_D]:
        print("D")
    if onkey[SDL_SCANCODE_SPACE]:
        print("Space")
    if onkey[SDL_SCANCODE_LCTRL]:
        print("Ctrl")

def commandLine():
    global debug
    cmd = str(input(""))
    
    if cmd == "debug":
        debug = not debug
        #render_objects() replace with renderstep equiv
    
    commandLine()
    
commandLine()

SDL_Quit()
