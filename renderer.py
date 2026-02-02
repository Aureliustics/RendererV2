import ctypes
import sys
from sdl2 import *
import sdl2.ext
import math
import time
'''
rules for codebase: use SCREAMING_SNAKE_CASE for constants
Do not commit if you are just testing, commit if progress on the renderer is made

https://lukems.github.io/py-sdl2/modules/index.html for docs

todo: Mouse movements for camera pitch and yaw instead of IJKL
'''

def choose_window_size():
    buttons = (SDL_MessageBoxButtonData * 3)(
        SDL_MessageBoxButtonData(0, 1, b"400x400"),
        SDL_MessageBoxButtonData(0, 2, b"600x600"),
        SDL_MessageBoxButtonData(0, 3, b"800x800"),
    )

    messagebox = SDL_MessageBoxData(
        SDL_MESSAGEBOX_INFORMATION,
        None,
        b"Window Size",
        b"Choose a window size",
        3,
        buttons,
        None
    )

    buttonid = ctypes.c_int()
    SDL_ShowMessageBox(messagebox, ctypes.byref(buttonid))

    return {1: 400, 2: 600, 3: 800}.get(buttonid.value, 400)  # default fallback

# raw = input("Enter window size (Enter for default): ").strip()
# WINDOW_SIZE = WINDOW_SIZE = int(raw) if raw else 400 # replace this with WINDOW_SIZE = choose_window_size() for a prompt. couldnt figure out input fields so presets for now
WIDTH = int(input("Enter window width (Enter for default): ").strip())
HEIGHT = int(input("Enter window height (Enter for default): ").strip())

WHITE = 0xFFFFFFFF
GREEN = 0x05871f
LIGHT_BLUE = 0x23accf
RED = 0xf70000
FOV = 90
scale = (HEIGHT / 2) / math.tan(math.radians(FOV) / 2) # the projective proj scaling factor (higher = less stretched, lower = more stretch)
last_delta_time = 0

# init the window
SDL_Init(SDL_INIT_VIDEO)
window = SDL_CreateWindow(
    b"Renderer V2",
    SDL_WINDOWPOS_CENTERED,
    SDL_WINDOWPOS_CENTERED,
    WIDTH, HEIGHT,
    SDL_WINDOW_SHOWN
)
renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED)
texture = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_ARGB8888, SDL_TEXTUREACCESS_STREAMING, WIDTH, HEIGHT)

# init frame buffer (think abt the frame buffer like a jiba image file, it stores pixel colour data from top left to bottom right of the screen)
# the frame buffer is just our 1 dimensional chunk of memory which we can tell SDL to interpret it as pixels. SDL then copies that to the GPU where it is displayed
framebuffer = (ctypes.c_uint32 * (WIDTH * HEIGHT))() # ctypes.c_uint32 since each pixel is a 32 bit int

def renderStep():
    # displaying the frame buffer onto the screen (do not remove)
    SDL_UpdateTexture(texture, None, framebuffer, WIDTH * 4) # copies buffer memory into SDL texture
    SDL_RenderClear(renderer) # clear last frame
    SDL_RenderCopy(renderer, texture, None, None) # draw the pixels to window
    SDL_RenderPresent(renderer) # present the pixels

def clear(colour = 0xFFFFFFFF):
    # fill each pixel with white by setting the memory to the framebuffer instead of iterating through 100s of thousands of pixels
    ctypes.memset(framebuffer, colour & 0xFF, WIDTH * HEIGHT * 4) # unironically 90fps -> 1700fps LMAO


def pixel(x, y, colour):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        framebuffer[y * WIDTH + x] = colour

# using bresenhams line algorithm we can determine how to rasterize each pixel in a line.
def draw_line(x0, y0, x1, y1, colour): # draw line using point intercept form
    dx = abs(x1 - x0) # dx = delta x (change in x/how far the line goes in x direction)
    dy = abs(y1 - y0) 
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1) # cast all to int (you cant have a fraction of a pixel)
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
'''
draw_line(0, 0, WIDTH - 1, HEIGHT - 1, GREEN) # testing a diagonal line
draw_line(WIDTH // 2, 0, WIDTH // 2, HEIGHT - 1, LIGHT_BLUE) # vertical line
draw_line(0, HEIGHT // 2, WIDTH - 1, HEIGHT // 2, RED)

renderStep()
'''
sprinting = False
debug = False
collision = True
flying = True

last_time = time.perf_counter()
frame_count = 0

camera_pos = [0, 0, -15]
object_rot = [0, 0]
move_speed = 0.25
near_clip = 0.01
far_clip = 100
aspect_ratio = WIDTH


Vertices = [
    [-1, -1, 1],  # vertex 0
    [1, -1, 1],   # vertex 1
    [1, 1, 1],    # vertex 2
    [-1, 1, 1],   # vertex 3
    [-1, -1, -1], # vertex 4
    [1, -1, -1],  # vertex 5
    [1, 1, -1],   # vertex 6
    [-1, 1, -1]   # vertex 7
]

# cube edges
edges = [  # this is basically the connection points, not the vertices
    [0, 1], [1, 2], [2, 3], [3, 0],  # front face
    [4, 5], [5, 6], [6, 7], [7, 4],  # back face
    [0, 4], [1, 5], [2, 6], [3, 7]   # connecting edges
]

objects = [
    {"position": [3, 0, -5], "collision": True}, # positions are in xyz format
    {"position": [-3, 0, -5], "collision": False},
    {"position": [-1.5, 3, -5], "collision": True},
    {"position": [-4, -4.5, -4], "collision": False}
]

def matrix_multiply(A, B):
    rows_A = len(A)
    cols_A = len(A[0])
    cols_B = len(B[0])

    C = [[0] * cols_B for _ in range(rows_A)]

    for i in range(rows_A):
        for j in range(cols_B):
            for k in range(cols_A):
                C[i][j] += A[i][k] * B[k][j]

    return C


def check_collision(new_position):
    x, y, z = new_position

    for obj in objects:
        if not obj.get("collision", True):
            continue  # skip objects without collision

        pos = obj["position"]

        # 1.5 to simulate player leg collision
        hitbox_size = 1.5

        # bounding box for cubes (but a lot more optimized this time)
        min_bound = [pos[0] - hitbox_size, pos[1] - hitbox_size, pos[2] - hitbox_size]
        max_bound = [pos[0] + hitbox_size, pos[1] + hitbox_size, pos[2] + hitbox_size]

        # check if new position is inside the hitbox
        if (min_bound[0] <= x <= max_bound[0] and
            min_bound[1] <= y <= max_bound[1] and
            min_bound[2] <= z <= max_bound[2]):
            return True  # collision detected

    return False  # no collision

def move_camera(direction, speed):
    global camera_pos, sprinting, move_speed, debug, collision, flying
    if direction == "forward" and not sprinting:
        new_position = [camera_pos[0], camera_pos[1], camera_pos[2] + speed]
    elif direction == "forward" and sprinting:
        if speed < 1:
            move_speed += 0.1
        new_position = [camera_pos[0], camera_pos[1], camera_pos[2] + speed]
    elif direction == "backward":
        sprinting = False
        new_position = [camera_pos[0], camera_pos[1], camera_pos[2] - speed]
    elif direction == "left":
        new_position = [camera_pos[0] - speed, camera_pos[1], camera_pos[2]]
    elif direction == "right":
        new_position = [camera_pos[0] + speed, camera_pos[1], camera_pos[2]]
    elif direction == "up" and flying:
        new_position = [camera_pos[0], camera_pos[1] - speed, camera_pos[2]]   # jump
    elif direction == "down" and flying:
        new_position = [camera_pos[0], camera_pos[1] + speed, camera_pos[2]]   # crouch
    else:
        return
    if not check_collision(new_position) or not collision:
        camera_pos = new_position
    if debug:
        print(camera_pos)

def rotate_object(axis, angle_change):
    global object_rot
    if axis == "X":
        object_rot[0] += angle_change
    elif axis == "Y":
        object_rot[1] += angle_change

    if debug == True:
        print("[Debug Logs]: " + str(camera_pos[0]) + "x " + str(camera_pos[1]) + "y " + str(camera_pos[2]) + "z" + " | Pitch: " + str(object_rot[0]) + " | Yaw: " + str(object_rot[1]) + " | Sprint: " + str(sprinting) + " | Speed: " + str(move_speed))

def rotate_camera(direction, degrees): # technically not rotating the camera, it only gives a camera rotation illusion if you are in the middle of the objs
    global objects, camera_pos, object_rot
    
    # calculate the center of the platform (average position of all blocks)
    platform_center = [0, 0, 0]
    for obj in objects:
        platform_center[0] += obj["position"][0]
        platform_center[1] += obj["position"][1]
        platform_center[2] += obj["position"][2]
    
    # find the average to get the center
    platform_center[0] /= len(objects)
    platform_center[1] /= len(objects)
    platform_center[2] /= len(objects)

    # define the rotation matrix for the requested direction
    rotation_matrix = None
    # if direction == "up" and object_rot[0] > -90: for up max lookup angle
    if direction == "up": # object_rot[0] = pitch
        rotation_matrix = [
            [1, 0, 0],
            [0, math.cos(math.radians(-degrees)), -math.sin(math.radians(-degrees))],
            [0, math.sin(math.radians(-degrees)), math.cos(math.radians(-degrees))]  # update to x axis rotation
        ]
        rotate_object("X", -2 * delta_time)  # counter act the world rotation with object rotation
    
    # elif direction == "down" and object_rot[0] < 28: for max lookdown angle
    elif direction == "down":
        rotation_matrix = [
            [1, 0, 0],
            [0, math.cos(math.radians(degrees)), -math.sin(math.radians(degrees))],
            [0, math.sin(math.radians(degrees)), math.cos(math.radians(degrees))]  # update to x axis rotation
        ]
        rotate_object("X", 2 * delta_time)  # counter act the world rotation with object rotation
        
    elif direction == "left":
        rotation_matrix = [
            [math.cos(math.radians(degrees)), 0, math.sin(math.radians(degrees))],
            [0, 1, 0],
            [-math.sin(math.radians(degrees)), 0, math.cos(math.radians(degrees))]  # update to y axis rotation
        ]
        rotate_object("Y", 2 * delta_time)  # counter act the world rotation with object rotation
        
    elif direction == "right":
        rotation_matrix = [
            [math.cos(math.radians(-degrees)), 0, math.sin(math.radians(-degrees))],
            [0, 1, 0],
            [-math.sin(math.radians(-degrees)), 0, math.cos(math.radians(-degrees))]  # update to y axis rotation
        ]
        rotate_object("Y", -2 * delta_time)  # counter act the world rotation with object rotation

    if rotation_matrix is None: # catch crash if rotation matrix is None
        return
    
    # loop through each block and apply the rotation
    for obj in objects:
        position = obj["position"]
        
        # translate the object so the center of the platform is at the origin
        translated_position = [
            position[0] - platform_center[0],
            position[1] - platform_center[1],
            position[2] - platform_center[2]
        ]

        # apply the rotation matrix to the translated position
        rotated_position = matrix_multiply(rotation_matrix, [
            [translated_position[0]],
            [translated_position[1]],
            [translated_position[2]]
        ])

        # translate the position back from the origin to the platform center
        new_position = [
            rotated_position[0][0] + platform_center[0],
            rotated_position[1][0] + platform_center[1],
            rotated_position[2][0] + platform_center[2]
        ]

        # update the objects position
        obj["position"] = new_position

def rotate_vertex(vertex_x, vertex_y, vertex_z, sin_pitch, cos_pitch, sin_yaw, cos_yaw):
    # rotate camera pitch (x axis)
    rotated_y = vertex_y * cos_pitch - vertex_z * sin_pitch
    rotated_z = vertex_y * sin_pitch + vertex_z * cos_pitch

    #rotate camera yaw (y axis)
    rotated_x = vertex_x * cos_yaw + rotated_z * sin_yaw
    rotated_z = -vertex_x * sin_yaw + rotated_z * cos_yaw

    return rotated_x, rotated_y, rotated_z

def render_objects(): # new render pipeline: now takes all objs, transforms the vertices, projects them to 2D, then rasterizes edges
    global frame_count, last_time
    clear()

    camera_x, camera_y, camera_z = camera_pos
    camera_pitch, camera_yaw = object_rot

    # optimized this so that it precalculates trig values once per frame
    sin_pitch = math.sin(math.radians(camera_pitch))
    cos_pitch = math.cos(math.radians(camera_pitch))
    sin_yaw = math.sin(math.radians(camera_yaw))
    cos_yaw = math.cos(math.radians(camera_yaw))

    # need the get to center of the screen to properly project
    screen_center_x = WIDTH // 2
    screen_center_y = HEIGHT // 2
    
    # calculate Z distance from camera for each object (for sorting block distance)
    objects_with_distance = []
    for obj in objects:
        position = obj["position"]
        dx = position[0] - camera_pos[0] # dx means distance x
        dy = position[1] - camera_pos[1] # dy means distance y
        dz = position[2] - camera_pos[2] # dz means distance z
        distance = math.sqrt(dx**2 + dy**2 + dz**2) # get euclidean distance
        objects_with_distance.append((obj, distance))
        
    '''
    # use bubble sort to sort by descending distance
    def bubble_sort_descending(arr):
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j][1] < arr[j + 1][1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]

    bubble_sort_descending(objects_with_distance)
    '''
    objects_with_distance.sort(key = lambda pair: pair[1], reverse = True) # replace bubblesort for timsort (cuz its built into py and faster)
    
    for obj, distance in objects_with_distance:
        object_x, object_y, object_z = obj["position"] # grab coordinates of the object

        projected_vertices = [None] * len(Vertices) # store the projected 2D pos for each vertex

        for vertex_index, (vertex_x, vertex_y, vertex_z) in enumerate(Vertices):
            # rotate based on orientation of camera
            rotated_x, rotated_y, rotated_z = rotate_vertex(vertex_x, vertex_y, vertex_z, sin_pitch, cos_pitch, sin_yaw, cos_yaw)

            # translate each vertex to camera space
            camera_space_x = rotated_x + object_x - camera_x
            camera_space_y = rotated_y + object_y - camera_y
            camera_space_z = rotated_z + object_z - camera_z

            # new clipping implemented for camera space system
            if camera_space_z <= near_clip or camera_space_z >= far_clip:
                continue

            # apply perspective projection then store the projected vertices
            screen_x = int((camera_space_x / camera_space_z) * scale + screen_center_x)
            screen_y = int((camera_space_y / camera_space_z) * scale + screen_center_y)

            projected_vertices[vertex_index] = (screen_x, screen_y)

        # draw each edge/connection points of the cube using projected vertices
        for edge_start, edge_end in edges:
            start_point = projected_vertices[edge_start]
            end_point = projected_vertices[edge_end]

            # only draw edges/connection points where both vertices are valid
            if start_point and end_point:
                draw_line(start_point[0], start_point[1], end_point[0], end_point[1], 0xFF000000)
    renderStep()

    frame_count += 1
    now = time.perf_counter()

    if now - last_time >= 1.0:
        fps = frame_count / (now - last_time)
        SDL_SetWindowTitle(window, f"Renderer V2 | FPS: {fps:.1f}".encode())
        frame_count = 0
        last_time = now

render_objects()  # render the initial frame

running = True
while running:
    delta_time = (time.perf_counter() - last_delta_time) * 100
    last_delta_time = time.perf_counter()

    event = SDL_Event()
    while SDL_PollEvent(ctypes.byref(event)):
        if event.type == SDL_QUIT:
            running = False
    # not great looking but i am still figuring out key inputs
    onkey = SDL_GetKeyboardState(None)
    if onkey[SDL_SCANCODE_W]: move_camera("forward", move_speed * delta_time)
    if onkey[SDL_SCANCODE_S]: move_camera("backward", move_speed * delta_time)
    if onkey[SDL_SCANCODE_A]: move_camera("left", move_speed * delta_time)
    if onkey[SDL_SCANCODE_D]: move_camera("right", move_speed * delta_time)
    if onkey[SDL_SCANCODE_SPACE]: move_camera("up", move_speed * delta_time)
    if onkey[SDL_SCANCODE_LCTRL]: move_camera("down", move_speed * delta_time)
    if onkey[SDL_SCANCODE_UP]: rotate_object("X",2 * delta_time)
    if onkey[SDL_SCANCODE_DOWN]: rotate_object("X",-2 * delta_time)
    if onkey[SDL_SCANCODE_LEFT]: rotate_object("Y",2 * delta_time)
    if onkey[SDL_SCANCODE_RIGHT]: rotate_object("Y",-2 * delta_time)
    if onkey[SDL_SCANCODE_I]: rotate_camera("up",2 * delta_time)
    if onkey[SDL_SCANCODE_K]: rotate_camera("down",2 * delta_time)
    if onkey[SDL_SCANCODE_J]: rotate_camera("left",2 * delta_time)
    if onkey[SDL_SCANCODE_L]: rotate_camera("right",2 * delta_time)
    render_objects()

SDL_Quit()
