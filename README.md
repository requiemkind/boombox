# Boombox Project
The Boombox Project is a terminal-based, illustrative boombox that I created. The idea behind it is to introduce myself not only as someone with an interest in programming, but also as someone who enjoys sharing their musical taste.
*Music player made for learning purposes.*

## DISCLAIMER
ALL songs included in this project are present solely because this code contains MY personal song list from MY Boombox. I am not claiming ownership, nor do I intend to infringe upon the copyrights of any of these songs. Once again, this project was created for the purpose of improving my programming skills, not for profit.

This project uses '[Just Playback](https://github.com/cheofusi/just_playback)', make sure you're on Python 3.9 or newer.

- Windows: Double-click `start.bat` to download requirements and start the app.
- Linux/Mac: Run `pip install -r requirements.txt` and then `python main.py`.

## Interfaces
When you start the Boombox, you can choose between two interfaces:
- **ASCII:** A retro ASCII-art boombox with visual buttons, volume, and autoplay indicators. Note: Autoplay in this version is visually different, but the controls are universal for both interfaces.
- **Legacy:** The first version of the Boombox Project. Kept as a memory.

Use Up and Down keys + enter to choose which Boombox version you want.

## Controls

- Enter: Play songs. If a song is already playing, it pauses.
- "<", ">" (or "," , ".", arrow keys to said direction also works): Switches the currently displayed song. If a song is playing, immediately starts the next song.
- "+" (or "="), "[", "-", "]": Increase/Decrease volume by 10% and 1% respectively.
- "y" to enable autoplay ('False' by default), and "n" for turning off.

## Adding your own music

Ways to download the mp3's:
- [loader.to](https://en.loader.to/4/), used in the first stages of the project.
- [MusicDownloader](https://github.com/FelipeSelhorst/MusicDownloader), a separate project created by a friend, that works along with the Boombox.

Just add your .mp3 files to the 'songs' folder and update the 'songs.json' file for custom display names.
- To add custom titles for songs in the json file, follow the order: {"(songfilename).mp3": "(song name display)"}. 'Author - Song' or vice versa is not mandatory in the 'display name' part.

## Status/NOTE
The core features are complete. This is the full project, it will be soon released, as I'm still gonna make one final review of the project. Also, the public release of this project will not include my personal playlist due to avoid copyright. The `songs` folder will be empty for you to add your own tracks.
