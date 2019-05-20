#!/usr/bin/env python
try:
    # Python2
    from Tkinter import *
    import Tkinter.scrolledtext as tkscrolled
except ImportError:
    # Python3
    from tkinter import *
    import tkinter.scrolledtext as tkscrolled

import platform
import os
import subprocess
import sys
import time

from shutil import copyfile
import zipfile
from tempfile import gettempdir


def linux_distribution():
    try:
        return platform.linux_distribution()
    except:
        return "N/A"


def get_os_info():
    os_info = {
        "dist": str(platform.dist()),
        "linux_distribution": linux_distribution(),
        "system": platform.system(),
        "machine": platform.machine(),
        "platform": platform.platform(),
        "uname": platform.uname(),
        "version": platform.version()
        # "mac_ver" : platform.mac_ver()
    }
    return os_info


# Golbal vars
bin_dir = os.path.join(os.getcwd(), "bin")
isWindows = False
youtubedl = os.path.join(bin_dir, "youtube-dl")
ffmpeg = os.path.join(bin_dir, "ffmpeg")
protocol_whitelist = " "
if get_os_info()['system'] == 'Windows':
    isWindows = True
    youtubedl = os.path.join(bin_dir, "youtube-dl.exe")
    ffmpeg = os.path.join(bin_dir, "ffmpeg.exe")
    protocol_whitelist = " -protocol_whitelist \"file,http,https,tcp,tls\" "

try:
    import requests
except ImportError:
    if isWindows:
        print (
            "\nError: requests package is not installed pleas run: python -m pip install requests\n")
    else:
        print ("\nError: requests package is not installed pleas run: sudo python -m pip install requests\n")
        exit(1)


# try:
#     import urllib3
# except ImportError:
#     if isWindows:
#         print ("\nError: urllib3 package is not installed pleas run: python -m pip install urllib3\n")
#     else:
#         print ("\nError: urllib3 package is not installed pleas run: sudo python -m pip install urllib3\n")
#         exit(1)
#
# urllib3.disable_warnings()


def check_pre_requirements():
    if not os.path.exists(bin_dir):
        os.makedirs(bin_dir)
    pre_requirements = {"python": True, "youtube_dl": False, "ffmpeg": False}
    if sys.version_info[0] >= 2:
        pre_requirements["python"] = False
        if not isWindows:
            if not os.path.exists(youtubedl):
                pre_requirements["youtube_dl"] = True
            if not os.path.exists(ffmpeg):
                pre_requirements["ffmpeg"] = True
            # else:
            # if not os.path.exists(ffmpeg):
            # os.symlink("/usr/bin/ffmpeg", ffmpeg)
        else:
            if not os.path.exists(youtubedl):
                pre_requirements["youtube_dl"] = True
            if not os.path.exists(ffmpeg):
                pre_requirements["ffmpeg"] = True
    return pre_requirements


def download_file(url, file_name):
    with open(file_name, "wb") as f:
        start_time = time.clock()
        print "Downloading %s" % os.path.basename(file_name)
        response = requests.get(url, allow_redirects=True, stream=True)
        total_length = response.headers.get('content-length')
        if total_length is None:  # no content length header
            f.write(response.content)
        else:
            dl = 0
            float_total_length = float(total_length)
            int_total_length = int(total_length)
            for data in response.iter_content(chunk_size=int_total_length / 100):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / int_total_length)
                sys.stdout.write("\r[%s%s] Doloaded %.3fMB out of %.3fMB @ %.3fKBs" % (
                    '=' * done, ' ' *
                    (50 - done), float(float(dl) / 1024 / 1024),
                    float(float_total_length / 1024 / 1024),
                    float(dl / (1024 * (time.clock() - start_time)))))
                sys.stdout.flush()
    f.close()
    print "\ndone"


def download_ffmpeg():
    if not isWindows:
        try:
            download_file(
                "https://storage.googleapis.com/any-uploads/ffmpeg", ffmpeg)
            os.chmod(ffmpeg, 509)
            print os.linesep
        except Exception as e:
            os.remove(youtubedl)
            raise Exception(str(e))

    else:
        download_file("https://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-latest-win64-static.zip",
                      os.path.join(gettempdir(), "ffmpeg.zip"))
        zip_ref = zipfile.ZipFile(os.path.join(
            gettempdir(), "ffmpeg.zip"), 'r')
        zip_ref.extractall(gettempdir())
        zip_ref.close()
        copyfile(os.path.join(gettempdir(),
                              "ffmpeg-latest-win64-static\\bin\\ffmpeg.exe"), ffmpeg)


def download_youtubedl():
    if not isWindows:
        try:
            download_file(
                "https://yt-dl.org/downloads/latest/youtube-dl", youtubedl)
            os.chmod(youtubedl, 509)
            print os.linesep
        except Exception as e:
            os.remove(youtubedl)
            raise Exception(str(e))
    else:
        try:
            download_file(
                "https://yt-dl.org/downloads/latest/youtube-dl.exe", youtubedl)
            print os.linesep
        except Exception as e:
            os.remove(youtubedl)
            raise Exception(str(e))


def process_youtube(video_url, server, log_level):
    try:
        print "Getting youtube stream..."
        cmd = youtubedl, "--list-formats", video_url
        sys.stdout = StdoutRedirector(t)
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        popen.wait()
        output = popen.stdout.readlines()
        print "Fetching relevant stream..."
        best = str(output[-1]).replace("b'", "").split(' ')[0]
        cmd = youtubedl, "-f", best, "-g", video_url
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        popen.wait()
        output = popen.stdout.read()
        output = str(output).replace("b'", "").replace("\n", "")
        ffmpeg_cmd = '{} -re -y -hide_banner -loglevel {}{}-i {} -c copy -an -bufsize 3M -crf 20 -preset ultrafast ' \
                     '-rtmp_live live -shortest -f flv -muxdelay 0.05 {}'.format(ffmpeg, log_level, protocol_whitelist,
                                                                                 output, server)
        os.system(ffmpeg_cmd)
    except Exception as e:
        print str(e.message)

root = Tk()

w = 530
h = 300
x = 500
y = 500
root.geometry("%dx%d+%d+%d" % (w, h, x, y))
#root.resizable(0, 0)
top = Frame(root)                       # Create frame to hold entrys
bottom = Frame(root)                    # Create frame to hold button
bottom2 = Frame(root)                   # Create frame to hold log window
top.pack()                              # Pack top frame
bottom2.pack()                          # pack bottom2 frame
bottom.pack(side=RIGHT, anchor="sw")    # Pack bottom frame


l1 = Label(top, text="Youtube URL:")
l1.pack(side=LEFT)
e1 = Entry(top)
e1.pack(side=LEFT)
l2 = Label(top, text="Remote System:")
l2.pack(side=LEFT)
e2 = Entry(top)
e2.pack(side=LEFT)

# l = Label(root)

t = tkscrolled.ScrolledText(bottom2, state='disabled', width=75, height=16)
t.pack()

old_stdout = sys.stdout
class StdoutRedirector(object):
    def __init__(self, text_area):
        self.text_area = text_area

    def write(self, str):
        self.text_area.insert(END, str)
        self.text_area.see(END)

def callback():
    t.delete("1.0", "end")
    sys.stdout = StdoutRedirector(t)
    t.configure(state='normal')
    if (e1.get() and e2.get()):

        youtube_url = e1.get()
        rtmp_server = e2.get()
        loglevel = "32"
        try:
            loglevel = sys.argv[3]
        except:
            pass
        pre_requirements = check_pre_requirements()
        if pre_requirements["python"]:
            raise Exception("Python 2 version is required.")
        if pre_requirements["youtube_dl"]:
            download_youtubedl()
        if pre_requirements["ffmpeg"]:
            download_ffmpeg()
        # print sys.argv[1], sys.argv[2]
        process_youtube(youtube_url, rtmp_server, loglevel)
    else:
        t.insert(END, """Usage: python {} <youtube_url> <rtmp_destination_server>
Exp: python {} https://www.youtube.com/watch?v=y7e-GC6oGhg rtmp://demo.site.com/live/stream""".format(
            os.path.basename(sys.argv[0]), os.path.basename(sys.argv[0])))
    t.configure(state='disabled')
    t.see(END)


b = Button(bottom, text="OK", command=callback)
b.pack(side=RIGHT)

root.mainloop()
