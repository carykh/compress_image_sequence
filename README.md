Searches the specified folder for image sequences, then uses ffmpeg to convert them into .mp4's, and then (optionally) deletes the original images.

Usage: Type this into the command prompt:

```
python compress.py path/to/folder
```

It will recursively search the subfolders of that folder! If there's a sequence of files anywhere that look like below, it launches an ffmpeg command to create an .mp4 video file with those frames.
```
glorp0711.png
glorp0712.png
glorp0713.png
```
(there's a string at the start that stays the same, a numeric part that counts up, and a string at the end (".png") that stays the same)

After that, it opens the .mp4 so the user can watch it and check for mistakes. Then it asks the user if they want to delete the original .pngs. (I almost always say "yes", beacuse the ultimate goal is to save filespace.) The end!

Note: It'll require you to click on any option 3 times. (So if you want a 24fps .mp4, you'll have to click on the "Yes .mp4! 24 fps" button three times, as it moves around on the screen. The reason I did this is, I didn't want accidental clicks (or double clicks) to cause any sort of file creation or deletion, since that's risky. Here, you have to be very deliberate to make decisions. Upon using this tool for a bit, though, I think this feature is pretty stupid and time-wasting. Oh well.
