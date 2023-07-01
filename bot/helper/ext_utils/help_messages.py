#!/usr/bin/env python3

YT_HELP_MESSAGE = """
<b>Send link along with command line</b>:
<code>/{cmd}</code> link -s -n new name -opt x:y|x1:y1

<b>By replying to link</b>:
<code>/{cmd}</code> -n  new name -z password -opt x:y|x1:y1

<b>New Name</b>: -n
<code>/{cmd}</code> link -n new name
Note: Don't add file extension

<b>Upload Custom Drive</b>: link -id -index
-id <code>drive_folder_link</code> or <code>drive_id</code> -index <code>https://anything.in/0:</code>
drive_id must be folder id and index must be url else it will not accept

<b>Quality Buttons</b>: -s
Incase default quality added from yt-dlp options using format option and you need to select quality for specific link or links with multi links feature.
<code>/{cmd}</code> link -s

<b>Zip</b>: -z password
<code>/{cmd}</code> link -z (zip)
<code>/{cmd}</code> link -z password (zip password protected)

<b>Options</b>: -opt
<code>/{cmd}</code> link -opt playliststart:^10|fragment_retries:^inf|matchtitle:S13|writesubtitles:true|live_from_start:true|postprocessor_args:{{"ffmpeg": ["-threads", "4"]}}|wait_for_video:(5, 100)
Note: Add `^` before integer or float, some values must be numeric and some string.
Like playlist_items:10 works with string, so no need to add `^` before the number but playlistend works only with integer so you must add `^` before the number like example above.
You can add tuple and dict also. Use double quotes inside dict.

<b>Multi links only by replying to first link</b>: -i
<code>/{cmd}</code> -i 10(number of links)

<b>Multi links within same upload directory only by replying to first link</b>: -m
<code>/{cmd}</code> -i 10(number of links) -m folder name

<b>Upload</b>: -up
<code>/{cmd}</code> link -up <code>rcl</code> (To select rclone config, remote and path)
You can directly add the upload path: -up remote:dir/subdir
If DEFAULT_UPLOAD is `rc` then you can pass up: `gd` to upload using gdrive tools to GDRIVE_ID.
If DEFAULT_UPLOAD is `gd` then you can pass up: `rc` to upload to RCLONE_PATH.
If you want to add path manually from your config (uploaded from usetting) add <code>mrcc:</code> before the path without space
<code>/{cmd}</code> link -up <code>mrcc:</code>main:dump

<b>Rclone Flags</b>: -rcf
<code>/{cmd}</code> link -up path|rcl -rcf --buffer-size:8M|--drive-starred-only|key|key:value
This will override all other flags except --exclude
Check here all <a href='https://rclone.org/flags/'>RcloneFlags</a>.

<b>Bulk Download</b>: -b
Bulk can be used by text message and by replying to text file contains links seperated by new line.
You can use it only by reply to message(text/file).
All options should be along with link!
Example:
link1 -n new name -up remote1:path1 -rcf |key:value|key:value
link2 -z -n new name -up remote2:path2
link3 -e -n new name -opt ytdlpoptions
Note: You can't add -m arg for some links only, do it for all links or use multi without bulk!
link pswd: pass(zip/unzip) opt: ytdlpoptions up: remote2:path2
Reply to this example by this cmd <code>/{cmd}</code> b(bulk)
You can set start and end of the links from the bulk with -b start:end or only end by -b :end or only start by -b start. The default start is from zero(first link) to inf.


Check all yt-dlp api options from this <a href='https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py#L184'>FILE</a> or use this <a href='https://t.me/mltb_official_channel/177'>script</a> to convert cli arguments to api options.
"""

MIRROR_HELP_MESSAGE = """
<b>🚩How to Mirror ?</b>
<code>/mirror1</code> [Link]
<b>Example :</b>
<code>/mirror1 https://sourceforge.net/projects/opengapps/files/arm64/20220215/open_gapps-arm64-11.0-pico-20220215.zip/download</code>

<b>🚩How to Mirror With Custom Name?</b>
<code>/mirror1</code> [Link] -n [New Name]
<b>Note : Add -n After Your Link</b>
<b>Example :</b>
<code>/mirror1 https://sourceforge.net/projects/opengapps/files/arm64/20220215/open_gapps-arm64-11.0-pico-20220215.zip/download -n X.zip</code>

<b>🚩How to ZIP or Archive Mirror?</b>
<code>/mirror1</code> [Your Link] -z 
<b>Note : Add -z After Your Link</b>
<b>Example :</b>
<code>/mirror1 https://speed.hetzner.de/100MB.bin -z</code>

<b>🚩How to UNZIP or Extract Mirror ?</b>
<code>/mirror1</code> [Your Link] -e
<b>Note : Add -e After Your Link</b>
<b>Example :</b>
<code>/mirror1 https://sourceforge.net/projects/opengapps/files/arm64/20220215/open_gapps-arm64-11.0-pico-20220215.zip/download -e</code>

<b>🚩How to UNZIP or Extract File With Password?</b>
<code>/mirror1</code> [Your Link] -e [password]
<b>Note : Add -e [password] After Your Link</b>
<b>Example :</b>
<code>/mirror1 https://www.mediafire.com/file/n41mxmkb7tu9mfz/Wallpaper.zip/file -e xDrive</code>
_____________________________________

<b>🚩How to Mirror With qBitTorrent?</b>
<b>Example :</b>
<code>/qbmirror1 https://yts.mx/torrent/download/063A8D1602B018CEF86F34FF540D69D29F46CBBA</code>
<b>Use Magnet Link :</b>
<code>/qbmirror1 magnet:?xt=urn:btih:d984f67af9917b214cd8b6048ab5624c7df6a07a&tr=https%3A%2F%2Facademictorrents.com%2Fannounce.php&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce</code>

<b>🚩How to Mirror Seeding & Selection File With qBitTorrent?</b>
<b>Note : Add -s or -d After [Your Link] or [Magnet Link]</b>
<b>-s = Selection File</b>
<b>-d = Seeding File</b>
<b>Example :</b>
<b>- For Selection Files</b>
<code>/qbmirror1 https://yts.mx/torrent/download/063A8D1602B018CEF86F34FF540D69D29F46CBBA -s</code>

<b>- For Seeding Files</b>
<code>/qbmirror1 https://yts.mx/torrent/download/063A8D1602B018CEF86F34FF540D69D29F46CBBA -d</code>
"""

RSS_HELP_MESSAGE = """
Use this format to add feed url:
Title1 link (required)
Title2 link -c cmd -inf xx -exf xx
Title3 link -c cmd -d ratio:time -z password

-c command + any arg
-inf For included words filter.
-exf For excluded words filter.

Example: Title https://www.rss-url.com inf: 1080 or 720 or 144p|mkv or mp4|hevc exf: flv or web|xxx opt: up: mrcc:remote:path/subdir rcf: --buffer-size:8M|key|key:value
This filter will parse links that it's titles contains `(1080 or 720 or 144p) and (mkv or mp4) and hevc` and doesn't conyain (flv or web) and xxx` words. You can add whatever you want.

Another example: inf:  1080  or 720p|.web. or .webrip.|hvec or x264. This will parse titles that contains ( 1080  or 720p) and (.web. or .webrip.) and (hvec or x264). I have added space before and after 1080 to avoid wrong matching. If this `10805695` number in title it will match 1080 if added 1080 without spaces after it.

Filter Notes:
1. | means and.
2. Add `or` between similar keys, you can add it between qualities or between extensions, so don't add filter like this f: 1080|mp4 or 720|web because this will parse 1080 and (mp4 or 720) and web ... not (1080 and mp4) or (720 and web)."
3. You can add `or` and `|` as much as you want."
4. Take look on title if it has static special character after or before the qualities or extensions or whatever and use them in filter to avoid wrong match.
Timeout: 60 sec.
"""

CLONE_HELP_MESSAGE = """
Send Gdrive|Gdot|Filepress|Filebee|Appdrive|Gdflix link or rclone path along with command or by replying to the link/rc_path by command.

<b>Multi links only by replying to first gdlink or rclone_path:</b>
<code>/{cmd}</code> -i 10(number of links/pathies)

<b>Gdrive:</b>
<code>/{cmd}</code> gdrivelink

<b>Upload Custom Drive</b>: link -id -index
-id <code>drive_folder_link</code> or <code>drive_id</code> -index <code>https://anything.in/0:</code>
drive_id must be folder id and index must be url else it will not accept

<b>Rclone:</b>
<code>/{cmd}</code> (rcl or rclone_path) -up (rcl or rclone_path) -rcf flagkey:flagvalue|flagkey|flagkey:flagvalue

Note: If -up not specified then rclone destination will be the RCLONE_PATH from config.env
"""

CATEGORY_HELP_MESSAGE = """
Reply to an active /{cmd} which was used to start the download or add gid along with {cmd}
This command mainly for change category incase you decided to change category from already added download.
But you can always use /{mir} with to select category before download start.

<b>Upload Custom Drive</b>
<code>/{cmd}</code> -id <code>drive_folder_link</code> or <code>drive_id</code> -index <code>https://anything.in/0:</code> gid or by replying to active download
drive_id must be folder id and index must be url else it will not accept
"""
