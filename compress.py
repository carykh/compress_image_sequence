import os
import pygame
import glob
import re
import subprocess
import sys
import numpy as np
import time

FILL_GAPS = False  # If the frame sequence goes img001.png, img004.png, should we have the first image hold for those 2 missing frames?
EXTEND_END_BY = 2 # how many extra seconds at the end should the .mp4 go on for?

MIN_CARE_ABOUT = 50
FOLDERS_TO_SKIP = ["Rubik's Cube"]
WAKE_UP_WHEN_I_SEE = ""
awoken = (WAKE_UP_WHEN_I_SEE == "")

_fps = [-1,24,30,60,6,12]

def getLastOfType(stri, boole):
    for i in range(len(stri)-1,-1,-1):
        if stri[i].isnumeric() == boole:
            return i
    return -1

def could_be_IS(filename):
    if filename[-4:] == ".png" and awoken:
        nums = ""
        non_nums = ""
        
        lastNum = getLastOfType(filename, True)
        if lastNum >= 0:
            lastPreNum = getLastOfType(filename[:lastNum+1], False)
            nums = filename[lastPreNum+1:lastNum+1]
            non_nums = filename[:lastPreNum+1]+"*"+filename[lastNum+1:]
            return int(nums), non_nums
        else:
            return -1, None
        
        """added_ast = False
        for i in range(len(filename)):
            ch = filename[i]
            if ch.isnumeric():
                nums += ch
                if not added_ast:
                    non_nums += "*"
                    added_ast = True
            else:
                non_nums += ch
        if len(nums) == 0:
            return -1, None
        return int(nums), non_nums"""
    return -1, None

def create_mp4(dicty, key, path, bc):
    if bc == 0:
        return
    fps = _fps[bc]
    keys_inner = list(dicty[key].keys())
    keys_inner.sort()
    dur = 1/fps
    f = open("ffmpeg_temp.txt","w+")
    for i in range(len(keys_inner)):
        rep_count = 1
        if FILL_GAPS and i < len(keys_inner)-1:
            rep_count = keys_inner[i+1]-keys_inner[i]
        if i == len(keys_inner)-1:
            rep_count += int(EXTEND_END_BY*fps)
                
        for rep in range(rep_count):
            f.write(f"file '{dicty[key][keys_inner[i]]}'\nduration {dur}\n")
    f.flush()
    f.close()
    
    new_path = os.path.join(path, key)
    output_path = new_path.replace("*","video").replace(".png",".mp4")
    command = f"ffmpeg -r {fps} -f concat -safe 0 -i ffmpeg_temp.txt -c:v libx264 -pix_fmt yuv420p \"{output_path}\""
    subprocess.call(command, shell=True)
    return output_path

def search(paths):
    global dicty
    global awoken
    
    if len(paths) == 0:
        return -1
    path = paths.pop(0)

    results = os.listdir(path) 
    dicty = {}
    for result in results:
        new_path = os.path.join(path,result)
        index, stri = could_be_IS(result)
        if index >= 0:
            if not awoken and WAKE_UP_WHEN_I_SEE in new_path:
                print("I am awoken! By "+new_path)
                awoken = True
        
            if stri not in dicty:
                dicty[stri] = {}
            dicty[stri][index] = new_path.replace("\\","/")
        if result not in FOLDERS_TO_SKIP and os.path.isdir(new_path):
            paths.insert(0, new_path)
            
    dicty_keys = list(dicty.keys())
    for key in dicty_keys:
        if len(list(dicty[key].keys())) < MIN_CARE_ABOUT:  # this image sequence is less than MIN_CARE_ABOUT images, don't bother.
            dicty.pop(key, None)
    getPreviews()

def getPreviews():
    global previews
    global preview_indices
    global preview_filenames
    
    previews = []
    preview_indices = []
    preview_filenames = []
    
    if len(list(dicty.keys())) >= 1:
        folder = dicty[getCurrentKey()]
        file_keys = list(folder.keys())
        file_keys.sort()
        shifts = [0,(len(file_keys)-3)//2,len(file_keys)-3]
        for p in range(3):
            for i in range(3):
                index = file_keys[shifts[p]+i]
                image = None
                try:
                    image = pygame.image.load(folder[index])
                except:
                    image = pygame.image.load("404.jpg")
                if not (image.get_width() >= 1):
                    image = pygame.image.load("404.jpg")
                w = 180
                h = 180/image.get_width()*image.get_height()
                small_image = pygame.transform.scale(image, (w, h))
                previews.append(small_image)
                preview_indices.append(index)
                preview_filenames.append(folder[index])
        
        isRendered = False
        clearButtonHistory()
        shuffleButtons()

def clearButtonHistory():
    button_history[:] = -1

def shuffleButtons():
    buttons[:] = 0
    n = 2 if isRendered else 5
    button_order = np.random.choice(10, n, replace=False)
    for b in range(n):
        buttons[button_order[b]] = b+1

def multiLine(stri, coor, font, col):
    limit = 0
    for i in range(len(stri)):
        text_test = font.render(stri[0:i], True, col)
        if text_test.get_rect()[2] > coor[2]:
            break
        else:
            limit = i+1
            
    text_final = font.render(stri[0:limit], True, col)
    display_surface.blit(text_final, (coor[0],coor[1]))
    if limit < len(stri):
        multiLine(stri[limit:], [coor[0],coor[1]+28,coor[2]], font, col)

def shiftDicty():
    dicty.pop(getCurrentKey(), None)
    getPreviews()

def getCurrentKey():
    return list(dicty.keys())[0]

def getLineTwo():
    global currentPath
    if len(dicty) >= 1:
        IC_count = f"({len(dicty[getCurrentKey()])} images)"
        if isRendered:
            start = "Got it."
            if video_creation_choice >= 1:
                start = ".mp4 file created and is playing right now! Review it."
            return f'{start} What should we do with the remaining .png files?  {IC_count}  {preview_filenames[0]}'
        else:
            return f'Should we make an .mp4 of this sequence?  {IC_count}  {preview_filenames[0]}'
    else:
        if len(paths) == 0:
            return 'Done searching.'
        else:
            currentPath = paths[0]
            return f'Currently searching: {currentPath}'

def finishedButtonClicks():
    for choice in range(len(_fps)):
        valid = True
        for b in range(3):
            if button_history[b] != choice:
                valid = False
        if valid:
            return choice
    return -1

def drawScreen():
    display_surface.fill((200,220,240))
    multiLine(f'Starting point: {startPath}', (20,20,960), font, (80,40,0))
    multiLine(getLineTwo(), (20,85,960), font, (80,40,0))
    if len(previews) >= 1:
        for p in range(len(previews)):
            x = p%5
            y = p//5
            ax = 10+200*x
            ay = 220+150*y
            display_surface.blit(previews[p],(ax,ay))
            multiLine(str(preview_indices[p]),(ax,ay-28,180), font, (0,40,80))
    
        y = 505
        
        button_colors = [[140,140,140],[255,0,0],[255,255,0],[0,255,0],[0,255,255],[255,0,255]]
        button_names = ["No .mp4"]
        for i in range(1,len(_fps)):
            button_names.append(f"Yes .mp4 {_fps[i]} fps")
        if isRendered:
            button_names = ["Keep pngs and continue","Delete pngs and continue","Keep pngs and quit"]
        for b in range(10):
            x = b*100+5
            pygame.draw.rect(display_surface,button_colors[buttons[b]], pygame.Rect(x, y, 90, 90))
            multiLine(button_names[buttons[b]],(x+5,y+10,80), font, (0,0,0))
        for b in range(3):
            bc = button_history[b]
            col = [0,0,0] if bc == -1 else button_colors[bc]
            pygame.draw.rect(display_surface, col, pygame.Rect(5+30*b, 605, 20, 20))
        
        bc = finishedButtonClicks()
        if bc >= 0:
            col = button_colors[bc]
            if isRendered:
                text = "Proceeding"
                if bc == 1:
                    file_count = len(list(dicty[getCurrentKey()].keys()))
                    text = f"Deleting {file_count} .png files"
            else:
                text = "No .mp4 will be created here."
                if bc >= 1:
                    text = f"RENDERING A {_fps[bc]}fps MP4 OF THIS FRAME SEQUENCE NOW!"
            pygame.draw.rect(display_surface, col, pygame.Rect(205, 605, 590, 90))
            multiLine(text,(300,630,400), font, (0,0,0))
    multiLine(f"Total .pngs deleted: {totalFilesDeletedCount}",(20,716,400), font, (0,0,0))
    pygame.display.update()
    
# "Z:/File Storage Extra/LC_test"
startPath = sys.argv[1]
paths = [startPath]
pygame.font.init()
pygame.font.get_init()
font = pygame.font.SysFont('Arial.ttf', 28)

currentPath = startPath
dicty = {}
search(paths)
W_W = 1000
W_H = 750
display_surface = pygame.display.set_mode((W_W, W_H))
previews = []
preview_filenames = []
preview_indices = []
BUTTON_COUNT = 10
buttons = np.zeros((BUTTON_COUNT), dtype=int)
button_history = np.zeros((3), dtype=int)
video_creation_choice = -1
isRendered = False
totalFilesDeletedCount = 0
while True:
    time.sleep(0.005)
    if len(dicty) == 0:
        search(paths)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.MOUSEBUTTONUP:
            mx, my = pygame.mouse.get_pos()
            if len(dicty) == 0:
                search(paths)
            else:
                if my >= 500 and my < 600:
                    button_history[0:2] = button_history[1:3]
                    button_history[2] = buttons[mx//100]
                    bc = finishedButtonClicks()
                    if bc >= 0:
                        drawScreen()
                        if isRendered:
                            isRendered = False
                            if bc == 0:
                                shiftDicty()
                            elif bc == 1:
                                key = getCurrentKey()
                                file_keys = list(dicty[key].keys())
                                for f in file_keys:
                                    filename = dicty[key][f]
                                    os.remove(filename)
                                    totalFilesDeletedCount += 1
                                shiftDicty()
                            elif bc == 2:
                                pygame.quit()
                                quit()
                            clearButtonHistory()
                        else:
                            video_creation_choice = bc
                            output_path = create_mp4(dicty,getCurrentKey(),currentPath,video_creation_choice)
                            isRendered = True
                            if bc >= 1:
                                os.startfile(output_path)
                            clearButtonHistory()
                            shuffleButtons()
                    else:
                        shuffleButtons()

    drawScreen()
        
