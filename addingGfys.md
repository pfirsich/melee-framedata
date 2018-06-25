# Adding gfys
Some of this is a tutorial, some of it is guidelines to end up with a consistent look for the gfys for each character. If you have suggestions for improvement, please tell me.

## Preparing an .iso
To color the hitboxes, I use a custom Gecko code that colors hitboxes based on the damage value. Also I patch the .iso file so that all hitbox damage values are replaced with their group id.

Therefore you need to add the Gecko code, which can be found here: [hitboxDamageAsColorId.txt](https://github.com/pfirsich/melee-framedata/blob/master/hitboxColors/hitboxDamageAsColorId.txt). And you also need to patch a 20XX Melee .iso (or some other .iso that enables you to render hitboxes, but I only tested it with [20XX Hack Pack 4.07++](https://smashboards.com/threads/the-20xx-melee-training-hack-pack-v4-07-7-04-17.351221/)).

You probably want to create a copy of your 20XX .iso because this process is very hard to reverse and setting most damage values to 0 will obviously make the game unplayable.

To patch the .iso you need Python 3 and you need to install the [gciso](https://github.com/pfirsich/gciso) library. Then navigate to `<melee-framedata>/hitboxColors` and call:
```console
python applyPatch.py patchData.json "<path to your .iso>"
```
or if you want to set gravity to zero (to avoid hitbox interpolation distorting the hitboxes from falling/rising) and disable grabs (so the grab hitboxes are not all rendered purple, but with the colors we assigned):
```console
python applyPatch.py patchData-zerogravity-disablegrabs.json "<path to possibly another .iso>"
```

### Alternative way
If you don't want to install Python or this seems to complicated for you, you can also use a tool like [GC Rebuilder](https://www.romhacking.net/utilities/619/) (or similar) or even the [gciso](https://github.com/pfirsich/gciso) command line interface (Python 3 still required though) and replace a single character .dat file with a patched version. I uploaded the patched character dat files here: [hitbox-damage-colors](http://melee.theshoemaker.de/?dir=hitbox-damage-colors).

## Recording
First turn on debug mode by pressing Pause and then D-Pad Right twice, then unpause with X + D-Pad Up.

If you are using the `--zerogravity` version:
* To Toggle frame advance on to not accidentally jump or something press the Pause button
* Open the player menu (D-Pad Down)
* Left Stick Right to switch to `P2`
* Set `CONTROLLED BY` to `P1` and `TYPE` to `HUMAN`
* Toggle frame advance off with Pause
* Airdodge down with both to get to the ground
* Then toggle frame advance on for safety again

Shared setup:
* Turn on hitbubbles rendered on top: R + D-Pad Up twice
* Turn off background: X + Down three times
* Infinite Shields: A + Down
* Toggle player menu on: D-Pad Down
* Set `P2` to `P2`/`CPU`/`20XX`/`SHIELD-HOLD`
* Toggle player menu off again: D-Pad Down
* Turn on action state display: Y + D-Pad Down

Then set up the camera, start from a neutral state (e.g. `FALL` or `WAIT`), toggle frame advance on (by pressing start) and make a screenshot for every frame of the move (make sure to include a frame of the neutral state at the start and the end of the move.

### Other notes
* The map I used, because it doesn't have an annoying background, enough space and a platform is `Hacked Stages -> Green Greens`
* For many moves using camera mode `Free` in `Training Mode` is sufficient, but sometimes you need to use the 20XX camera toggles (pan/zoom/rotate). These only work in `VS. Mode/Melee` though!
* With `--zerogravity` you should probably airdodge onto a platform at the start and then just walk off to record aerial moves.
* Record facing right, so the angle indicators are correct
* Record throws without `--zerogravity` and without `--disablegrabs` (only patched hitbox colors) (so you can actually grab another character and to make them fly representatively)
* Record aerials with the `--zerogravity` version (also aerial specials)
* Record grabs with the `--disablegrabs` version (so the hitboxes are not just always purple)
* [20XX Toggles](https://www.reddit.com/r/smashbros/comments/7ecgaj/20xx_407_complete_cheat_sheet_with_all_shortcut/)

## Turning the screenshots into videos
I highly recommend placing the screenshots for each move in a separate folder. Then you need to rename them `1.png`, `2.png`, `..`. I used some Python helper scripts for this, which you can find here:

https://gist.github.com/pfirsich/5e8e5fff777f7f426d88591ade7db44b

Then you need to turn these images into videos for which I used [ffmpeg](https://www.ffmpeg.org/), which I consider to be another wonder of the world, like so:

```console
ffmpeg -r 60 -i "<source directory>/%d.png" -y -c:v libx264 -vf "format=yuv420p" -r 60 "<outfile>.mp4"
```
* `-r 60` sets the rate of input screenshots to 60 fps.
* `-i "<source directory>/%d.png"` insert the path to the directory containing the screenshots here.
* `-y` tells ffmpeg to overwrite the output file without asking.
* `-c:v libx264` sets the output encoding to x264.
* `-vf "format=yuv420p"` sets the pixel format.
* `-r 60` sets the output rate of the video to 60 fps.
* `"<outfile>.mp4"` replace this with the name of the output file.

## Getting it on the website
When you have a folder full of videos, you can make an account on [gfycat.com](https://gfycat.com/) and upload them there.

To add them to the move pages you can either open an issue on the GitHub issue tracker (or send me an E-Mail) with a link to the gfycat album, or you can add it yourself by forking this repository, modifying the config file for the character you want to add gfys for (Example: [Samus' config](https://github.com/pfirsich/melee-framedata/blob/master/source/Samus/config.yaml)) and sending a pull request (obviously this is less work for me and therefore preferred)!

## Including specials
For specials most of this is the same, but as you might have noticed the special move pages for most characters lead to a `404 - Not Found`. This is because for most characters it is not configured which subactions belong to which special. You may add that information to the character configs (see [Samus' config](https://github.com/pfirsich/melee-framedata/blob/master/source/Samus/config.yaml) on how that would look). Also you may extend [meleeFrameDataExtractor](https://github.com/pfirsich/meleeFrameDataExtractor) (see ToDo) with proper subaction names, instead of just the hex ids.

