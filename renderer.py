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

# init frame buffer (think abt the frame buffer like a jiba image file, it stores pixel colour data from top left to bottom right of the screen)
# the frame buffer is just our 1 dimensional chunk of memory which we can tell SDL to interpret it as pixels. SDL then copies that to the GPU where it is displayed
framebuffer = (ctypes.c_uint32 * (WIDTH * HEIGHT))() # ctypes.c_uint32 since each pixel is a 32 bit int

def renderStep():
    # displaying the frame buffer onto the screen (do not remove)
    SDL_UpdateTexture(texture, None, framebuffer, WIDTH * 4) # copies buffer memory into SDL texture
    SDL_RenderClear(renderer) # clear last frame
    SDL_RenderCopy(renderer, texture, None, None) # draw the pixels to window
    SDL_RenderPresent(renderer) # present the pixels

def clear():
# fill each pixel with white, could prob make this the clear function later too
    for i in range(WIDTH * HEIGHT):
        framebuffer[i] = WHITE  # white in argb (alpha, red, green, blue)
    renderStep()
clear()

def pixel(x, y, colour):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        framebuffer[y * WIDTH + x] = colour

# using bresenhams line algorithm we can determine how to rasterize each pixel in a line.
def draw_line(x0, y0, x1, y1, colour): # draw line using point intercept form
    x0 = int(x0)
    y0 = int(y0)
    x1 = int(x1)
    x0 = int(x0)
    dx = abs(x1 - x0) # dx = delta x (change in x/how far the line goes in x direction)
    dy = abs(y1 - y0) 
    sx = 1 if x0 < x1 else -1 # sx (step x) to step right (1) when x1 better than x0 else step left (-1) 
    sy = 1 if y0 < y1 else -1 # sy (step y) to step up (1) when x1 better than x0 else step down (-1) 
    err = dx - dy

    while True:
        pixel(x0, y0, colour)
        if x0 == x1 and y0 == y1: # if end point is reached, stop drawing
            break
        # err or the error term is how much the line deviates from a perfect mathematical line
        e2 = 2 * err # double to avoid floats which are costly in performance
        if e2 > -dy: # if error is large enough to step into x dir
            err -= dy
            x0 += sx
        if e2 < dx: # if error is large enough to step into y dir
            err += dx
            y0 += sy

draw_line(0, 0, WIDTH - 1, HEIGHT - 1, GREEN) # testing a diagonal line
renderStep()

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
        draw_line(int(WIDTH / 2), 0, int(WIDTH / 2), HEIGHT - 1, LIGHT_BLUE) # testing a diagonal line
        renderStep()
    if onkey[SDL_SCANCODE_S]:
        print("S")
        draw_line(100, 100, 300, 100, LIGHT_BLUE) # testing a diagonal line
        draw_line(300, 100, 300, 300, LIGHT_BLUE) # testing a diagonal line
        draw_line(300, 300, 100, 300, LIGHT_BLUE) # testing a diagonal line
        draw_line(100, 300.67, 100, 100, LIGHT_BLUE) # testing a diagonal line
        renderStep()
    if onkey[SDL_SCANCODE_A]:
        print("A")
        clear()
        renderStep()
    if onkey[SDL_SCANCODE_D]:
        print("D")
    if onkey[SDL_SCANCODE_SPACE]:
        print("Space")
    if onkey[SDL_SCANCODE_LCTRL]:
        print("Ctrl")
''' uhh change this later or it will hang cuz its an infinite recursion
def commandLine():
    global debug
    cmd = str(input(""))
    
    if cmd == "debug":
        debug = not debug
        #render_objects() replace with renderstep equiv
    
    commandLine()
    
commandLine()
'''
SDL_Quit()
