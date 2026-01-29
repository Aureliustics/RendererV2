import renderer

'''
To call variables and functions form the renderer.py file, you need to first write "render." followed by whatever resource you want to access.
For exmaple: render.objects or renderer.render_objects
'''

def times_of_day():
    global daytime
    daytime = not daytime
    if daytime == True:
        #bgcolor("light blue")
        print("[World]: It is now day time.")
    else:
        #bgcolor("black")
        print("[World]: It is now night time.")
    #screen.ontimer(times_of_day, 60000) # function recursion to keep changing time of day every min

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

        #block_color = colors[0] # first item in colour list, aka green. we can add more colours to the list later for stone n stuff

        renderer.objects.append({
            "position": [x, y, z],
            "collision": True
            #"color": block_color
        })

renderer.render_objects