# This is the original renderer code that was used in CodeHS, refer to it if needed.

import math

print("Keyboard interaction: \n1. WASD to move camera\n2. IJKL to adjust pitch and yaw\n3. Arrow keys to adjust rotations\n")

# canvas setup
window_length_input = input("Set window size (Press enter for default): ")

window_length = int(window_length_input) if window_length_input else 400

screen = getscreen()
screen.setup(window_length, window_length)
shape("turtle")

speed(0)
bgcolor("white")
hideturtle()

# camera position and rotation
camera_pos = [0, 0, -15]  # camera position in 3D space, -5z starting pos and 1y
object_rot = [0, 0]  # camera rotation (pitch, yaw)
move_speed = 0.5  # movement speed
near_clip = 0.01  # near clipping plane. lower = cube has to be closer before clipping logic sets in, further = cube will clip from further
far_clip = 100  # far clipping plane
aspect_ratio = window_length  # screen aspect ratio.
#camera_turn = [0, 0]  # camera panning (x, y). not yet implemented cuz im using the rotate world method
#fov = 120  # field of view

# game controls/game environment
sprinting = False # off by default
debug = False # for printing data to console. like sprint, or object rotations
collision = True  # toggle this when you want collision on/off
daytime = True # controlled via the ontimer thingy
flying = True # not yet implemented. will be enabled for creative, disabled for survival ofc
isGrounded = False # false by default so u fall a bit on spawn. not yet implemented. for gravity later

def sprint():  # maybe make this toggle not hold to prevent bugs
    global sprinting
    sprinting = not sprinting  # sprint logic should check if using W key only and if stopped, set speed back to 0
    render_objects() # refresh for the sprint ui

def game_ui(): # initialized the game ui, such as hotbar, coords, viewmodel/hand, etc
    global sprinting
    # draw crosshair
    penup()
    seth(0)
    setposition(0,0)
    pendown()
    color("white")
    pensize(2)

    for i in range(2):
        forward(25 / 2)
        backward(50 / 2)
        forward(25 / 2)
        left(90)
    penup()
    pensize(1)
    seth(0)
    
    
    coord_x = -window_length / 2 + 10  # dynamically calculate where to put coordinate text to scale with screen size
    coord_y = -window_length / 2 + 10 
    # display coordinates
    setposition(coord_x, coord_y) # make this dynamically scale based on length later
    write(str(camera_pos[0]) + "x " + str(camera_pos[1]) + "y " + str(camera_pos[2]) + "z", move=False, align="top", font=("Lucida Console", 9, "normal"))
    # display if sprinting
    if sprinting == True:
        sprint_x = window_length / 2 - 90  # positioning sprint text to the right side
        sprint_y = -window_length / 2 + 10  # keep it vertically aligned
        setposition(sprint_x, sprint_y)
        write("(Sprinting)", move=False, align="top", font=("Lucida Console", 9, "normal"))
    
def times_of_day():
    global daytime
    daytime = not daytime
    if daytime == True:
        bgcolor("light blue")
        print("[World]: It is now day time.")
    else:
        bgcolor("black")
        print("[World]: It is now night time.")
    screen.ontimer(times_of_day, 60000) # function recursion to keep changing time of day every min

#screen.ontimer(times_of_day, 60000) # switch every minute

# cube vertices
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

# basic world generation. spawn a 5x5 platform under camera

colors = ["green", "#794d0d", "grey"]  # 794d0d is dirt colour
''' commented out platoform because its for a different demonstration
platform_size = 9
spacing = 2  # distance between cubes
start_x = -(platform_size // 2) * spacing
start_z = -(platform_size // 2) * spacing

# later instead of 2 for loops, just add a Y value checker so you know which layer is dirt coloured, and which is grass
for i in range(platform_size): # draw grass layer
    for j in range(platform_size):
        x = start_x + i * spacing
        z = start_z + j * spacing
        y = -3  # beneath the camera

        block_color = colors[0] # first item in colour list, aka green. we can add more colours to the list later for stone n stuff

        objects.append({
            "position": [x, y, z],
            "collision": True,
            "color": block_color
        })
'''
# matrix multiplication for transforming x,y to x,y,z for depth
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
        if not obj.get("collision", True):  # skip collision code if object has collision attribute set to False
            continue

        position = obj["position"]

        # side faces need larger hitboxes because it looks like it needs more space for some reason
        hitbox_size = 1.5
        side_hitbox_size = 2.0
        
        # seperate top and bottom hitbox. top larger to act as player hitbox. scuffed but works
        top_hitbox_size = 2.5  # this makes it so u cant fall below 1y when standing on a block
        bottom_hitbox_size = 2.0

        # front and back faces bounding box
        cube_min_front_back = [position[0] - hitbox_size, position[1] - hitbox_size, position[2] - hitbox_size]
        cube_max_front_back = [position[0] + hitbox_size, position[1] + hitbox_size, position[2] + hitbox_size]
        
        # side faces bounding box
        cube_min_sides = [position[0] - side_hitbox_size, position[1] - hitbox_size, position[2] - hitbox_size]
        cube_max_sides = [position[0] + side_hitbox_size, position[1] + hitbox_size, position[2] + hitbox_size]
        
        # top face bounding box
        cube_min_top = [position[0] - hitbox_size, position[1] + hitbox_size, position[2] - hitbox_size]
        cube_max_top = [position[0] + hitbox_size, position[1] + hitbox_size + top_hitbox_size, position[2] + hitbox_size]

        # bottom face bounding box
        cube_min_bottom = [position[0] - hitbox_size, position[1] - bottom_hitbox_size, position[2] - hitbox_size]
        cube_max_bottom = [position[0] + hitbox_size, position[1] - hitbox_size, position[2] + hitbox_size]
        
        # check for collisions with the front/back face
        if (cube_min_front_back[0] < x < cube_max_front_back[0] and
            cube_min_front_back[1] < y < cube_max_front_back[1] and
            cube_min_front_back[2] < z < cube_max_front_back[2]):
            return True
        
        # check for collisions with the side faces
        elif (cube_min_sides[0] < x < cube_max_sides[0] and
              cube_min_sides[1] < y < cube_max_sides[1] and
              cube_min_sides[2] < z < cube_max_sides[2]):
            return True
        
        # check for collisions with the top face
        elif (cube_min_top[0] < x < cube_max_top[0] and
              cube_min_top[1] < y < cube_max_top[1] and
              cube_min_top[2] < z < cube_max_top[2]):
            return True
        
        # check for collisions with the bottom face
        elif (cube_min_bottom[0] < x < cube_max_bottom[0] and
              cube_min_bottom[1] < y < cube_max_bottom[1] and
              cube_min_bottom[2] < z < cube_max_bottom[2]):
            return True

    return False

# basically player movement
def move_camera(direction, speed):
    global camera_pos, sprinting, move_speed, debug, collision, flying

    original_position = camera_pos[:]  # buffer original position before movement. used for collision check

    if direction == "forward" and sprinting == False:
        move_speed = 0.5  # if not sprinting then set speed back to default
        new_position = [camera_pos[0], camera_pos[1], camera_pos[2] + move_speed] # camera_pos has 3 values, [0] = x [1] = y, [2] = z

    elif direction == "forward" and sprinting == True:
        if speed < 1:  # max speed cap
            move_speed += 0.1  # accelerate by 0.1 each time
        new_position = [camera_pos[0], camera_pos[1], camera_pos[2] + move_speed]

    elif direction == "backward":
        sprinting = False  # toggle off sprinting
        move_speed = 0.5  # reset sprint when clicking S key like in minecraft
        new_position = [camera_pos[0], camera_pos[1], camera_pos[2] - move_speed]
    elif direction == "left":
        new_position = [camera_pos[0] - move_speed, camera_pos[1], camera_pos[2]]
    elif direction == "right":
        new_position = [camera_pos[0] + move_speed, camera_pos[1], camera_pos[2]]
        
    elif direction == "up" and flying == True:
        new_position = [camera_pos[0], camera_pos[1] + move_speed, camera_pos[2]]
    elif direction == "down" and flying == True:
        # prevent camera from colliding with the floor in flying mode (optional)
        new_position = [camera_pos[0], camera_pos[1] - move_speed, camera_pos[2]]

    if not check_collision(new_position) or collision == False:
        camera_pos = new_position  # if there is no collision then update position

    if debug == True:
        print("[Debug Logs]: " + str(camera_pos[0]) + "x " + str(camera_pos[1]) + "y " + str(camera_pos[2]) + "z" + " | Pitch: " + str(object_rot[0]) + " | Yaw: " + str(object_rot[1]) + " | Sprint: " + str(sprinting) + " | Speed: " + str(move_speed))
    render_objects()

# rotate camera along X or Y axis
def rotate_object(axis, angle_change):
    global object_rot
    if axis == "X":
        object_rot[0] += angle_change
    elif axis == "Y":
        object_rot[1] += angle_change

    if debug == True:
        print("[Debug Logs]: " + str(camera_pos[0]) + "x " + str(camera_pos[1]) + "y " + str(camera_pos[2]) + "z" + " | Pitch: " + str(object_rot[0]) + " | Yaw: " + str(object_rot[1]) + " | Sprint: " + str(sprinting) + " | Speed: " + str(move_speed))
    render_objects()


def rotate_camera(direction, degrees):
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
    if direction == "up" and object_rot[0] > -90: # object_rot[0] = pitch
        rotation_matrix = [
            [1, 0, 0],
            [0, math.cos(math.radians(-degrees)), -math.sin(math.radians(-degrees))],
            [0, math.sin(math.radians(-degrees)), math.cos(math.radians(-degrees))]  # update to x axis rotation
        ]
        rotate_object("X", -2)  # counter act the world rotation with object rotation
        
    elif direction == "down" and object_rot[0] < 28:
        rotation_matrix = [
            [1, 0, 0],
            [0, math.cos(math.radians(degrees)), -math.sin(math.radians(degrees))],
            [0, math.sin(math.radians(degrees)), math.cos(math.radians(degrees))]  # update to x axis rotation
        ]
        rotate_object("X", 2)  # counter act the world rotation with object rotation
        
    elif direction == "left":
        rotation_matrix = [
            [math.cos(math.radians(degrees)), 0, math.sin(math.radians(degrees))],
            [0, 1, 0],
            [-math.sin(math.radians(degrees)), 0, math.cos(math.radians(degrees))]  # update to y axis rotation
        ]
        rotate_object("Y", 2)  # counter act the world rotation with object rotation
        
    elif direction == "right":
        rotation_matrix = [
            [math.cos(math.radians(-degrees)), 0, math.sin(math.radians(-degrees))],
            [0, 1, 0],
            [-math.sin(math.radians(-degrees)), 0, math.cos(math.radians(-degrees))]  # update to y axis rotation
        ]
        rotate_object("Y", -2)  # counter act the world rotation with object rotation

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

    render_objects()
    
    
# render all objects based on camera position and rotation
def render_objects():
    clear()
    screen.tracer(0)
    
    # calculate rotation matrices for X and Y axis
    rotationX = [[1, 0, 0],
                 [0, math.cos(math.radians(object_rot[0])), -math.sin(math.radians(object_rot[0]))],
                 [0, math.sin(math.radians(object_rot[0])), math.cos(math.radians(object_rot[0]))]]

    rotationY = [[math.cos(math.radians(object_rot[1])), 0, math.sin(math.radians(object_rot[1]))],
                 [0, 1, 0],
                 [-math.sin(math.radians(object_rot[1])), 0, math.cos(math.radians(object_rot[1]))]]
    
    # calculate Z distance from camera for each object (for sorting block distance)
    objects_with_distance = []
    for obj in objects:
        position = obj["position"]
        dx = position[0] - camera_pos[0] # dx means distance x
        dy = position[1] - camera_pos[1] # dy means distance y
        dz = position[2] - camera_pos[2] # dz means distance z
        distance = math.sqrt(dx**2 + dy**2 + dz**2) # get euclidean distance
        objects_with_distance.append((obj, distance))

    # use bubble sort to sort by descending distance
    def bubble_sort_descending(arr):
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j][1] < arr[j + 1][1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]

    bubble_sort_descending(objects_with_distance)

    '''
    def partition(arr, low, high):
        pivot = arr[high]
        i = low - 1
        for j in range(low, high):
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1
    
    def quick_sort(arr, low, high):
        if low < high:
            p = partition(arr, low, high)
            quick_sort(arr, low, p - 1)
            quick_sort(arr, p + 1, high)
    
    print(objects_with_distance)
    quick_sort(objects_with_distance, 0, len(objects_with_distance) - 1)
    '''
    # get sorted objects
    sorted_objects = [obj for obj, i in objects_with_distance]
    
    # loop apply matrix math, clipping, and colour to each object
    for obj in sorted_objects:
        position = obj["position"]
        projected_vertices = []
        # loop through vertices and translate 3d matrix to 2d
        for Vertex in Vertices:
            xRotation = matrix_multiply(rotationX, [[Vertex[0]], [Vertex[1]], [Vertex[2]]])
            yRotation = matrix_multiply(rotationY, xRotation)
            # apply camera translation
            xPos = yRotation[0][0] + position[0] - camera_pos[0]
            yPos = yRotation[1][0] + position[1] - camera_pos[1]
            zPos = yRotation[2][0] + position[2] - camera_pos[2]
            # apply perspective projection. i didnt use the perspective_projection() function here
            if zPos != 0:
                x_screen = (xPos / zPos) * 300  # you can increase or decrease the multiplier to adjust scale
                y_screen = (yPos / zPos) * 300 # I found that increasing this from 100 to 300 made the fov stretch less extreme
            else:
                x_screen, y_screen = 0, 0
            # apply clipping. without this you will see 2 objects, if its half way clipped.
            if zPos < near_clip or zPos > far_clip: 
                continue
            # store projected vertex
            projected_vertices.append([x_screen, y_screen, zPos])
        
        face_color = obj.get("color", "white") # later add another attribute for colour for each individual block
        faces = [
            [0, 1, 2, 3],  # front face
            [4, 5, 6, 7],  # back face
            [0, 1, 5, 4],  # bottom face
            [2, 3, 7, 6],  # top face
            [0, 3, 7, 4],  # left face
            [1, 2, 6, 5]   # right face
        ]
        
        for face in faces:  # do for each face of object
            # getting each vertex of each face
            try:
                p1, p2, p3, p4 = [projected_vertices[idx] for idx in face]
            except IndexError:
                continue  # skip face if it has been despawned/clipped
        
            # check if any vertex is invalid or out of the clipping range (z < near_clip or z > far_clip)
            invalid_face = False
            for p in [p1, p2, p3, p4]:
                if p is None or p[2] < near_clip or p[2] > far_clip:
                    invalid_face = True
                    break
        
            if invalid_face:
                continue  # skip rendering this face if any vertex is invalid or out of range
        
            # fill each face with solid colour
            begin_fill()
            color(face_color)
        
            penup()
            setposition(p1[0], p1[1])  # just like old connection points
            penup()
            setposition(p2[0], p2[1])
            setposition(p3[0], p3[1])
            setposition(p4[0], p4[1])
            setposition(p1[0], p1[1])
            penup()
            end_fill()
   
        for edge in edges: # basically connection points. thats what edges are
            p1_idx, p2_idx = edge # idx means index
            if p1_idx < len(projected_vertices) and p2_idx < len(projected_vertices):
                p1 = projected_vertices[p1_idx]
                p2 = projected_vertices[p2_idx]
                penup()
                setposition(p1[0], p1[1])
                pendown()
                color("black")  # set the edge color to black, later set it to darker than main colour
                setposition(p2[0], p2[1])
                penup()
                
        if debug:
            collision_text = "Collision Enabled" if obj.get("collision", True) else "Collision Disabled"
            label_color = "green" if obj.get("collision", True) else "red"
            penup()
            color(label_color)
            write(collision_text, align="left", font=("Lucida Console", 9, "normal"))
            penup()
    # clear screen if no vertices are visible
    if len(projected_vertices) == 0:
        clear()
    penup()
    #game_ui() # call game ui, this will include hotbar, crosshair, health, armour, food, view model etc
    screen.update()

render_objects()  # render the initial frame

def keyInput():
    screen.listen()

    # player movement bindings (along the xyz axis)
    screen.onkey(lambda: move_camera("forward", move_speed), "w")
    screen.onkey(lambda: move_camera("backward", move_speed), "s")
    screen.onkey(lambda: move_camera("left", move_speed), "a")
    screen.onkey(lambda: move_camera("right", move_speed), "d")
    screen.onkey(lambda: move_camera("up", move_speed), "Space")
    screen.onkey(lambda: move_camera("down", move_speed), "Control")

    # object rotations. probably dont use this. its the old rotation code from renderer v2
    screen.onkey(lambda: rotate_object("X", 2), "Up")
    screen.onkey(lambda: rotate_object("X", -2), "Down")
    screen.onkey(lambda: rotate_object("Y", 2), "Right")
    screen.onkey(lambda: rotate_object("Y", -2), "Left")
    
    # camera panning binds (looking left right up down) vertical panning fixed to 90 and -90.
    screen.onkey(lambda: rotate_camera("up", 2), "i")
    screen.onkey(lambda: rotate_camera("left", 2), "j")
    screen.onkey(lambda: rotate_camera("down", 2), "k")
    screen.onkey(lambda: rotate_camera("right", 2), "l")
    
    # sprint toggle
    screen.onkey(lambda: sprint(), "Shift")

keyInput()
hideturtle()

def commandLine():
    global debug
    cmd = str(input(""))
    
    if cmd == "debug":
        debug = not debug
        render_objects()
    
    commandLine()
    
commandLine()

screen.mainloop()