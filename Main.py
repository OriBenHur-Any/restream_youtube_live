import platform
import os
import sys
import subprocess
import time
import urllib
import time
from tempfile import gettempdir


def linux_distribution():
  try:
    return platform.linux_distribution()
  except:
    return "N/A"
    
def reporthook(count, block_size, total_size):
    global start_time
    if count == 0:
        start_time = time.time()
        return
    duration = time.time() - start_time
    progress_size = int(count * block_size)
    speed = int(progress_size / (1024 * duration))
    percent = min(int(count*block_size*100/total_size),100)
    sys.stdout.write("\r%d%%, %d MB, %d KB/s, %d seconds passed" %
                    (percent, progress_size / (1024 * 1024), speed, duration))
    sys.stdout.flush()

def download_file(url, filename):
    urllib.urlretrieve(url, filename, reporthook)

def get_os_info():
  os_info= {
  "dist" : str(platform.dist()),
  "linux_distribution" : linux_distribution(),
  "system" : platform.system(),
  "machine" : platform.machine(),
  "platform" : platform.platform(),
  "uname" : platform.uname(),
  "version" : platform.version()
  #"mac_ver" : platform.mac_ver()
  }
  return os_info

if sys.version_info[0] > 2:
  raise Exception("Python 2 version is required.")

def download_youtubedl():
  if get_os_info()['system'] != 'Windows':
    dlfile = os.path.join(gettempdir(),"youtube-dl")
    try:
      print "Downloading youtube-dl"
      download_file("https://yt-dl.org/downloads/latest/youtube-dl", dlfile)
      print os.linesep
      return str("/tmp/youtube-dl"), True 
    except Exception as e:
      raise Exception(str(e))
  else:
    dlfile = os.path.join(gettempdir(),"youtube-dl.exe")
    try:
      print "Downloading youtube-dl.exe"
      download_file("https://yt-dl.org/downloads/latest/youtube-dl.exe", dlfile)
      print os.linesep
      return str(os.path.join(gettempdir(),"youtube-dl")), False 
    except Exception as e:
      raise Exception(str(e))

def proccess_youtube(video_url):
  binfile = download_youtubedl()
  cmd = binfile[0], "--list-formats", video_url
  if binfile[1]:
    os.chmod(binfile[0], 509)
  print "Getting youtube stream..."
  popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
  popen.wait()
  output = popen.stdout.readlines()
  best = str(output[-1]).replace("b'","").split(' ')[0]
  cmd = binfile[0] ,"-f", best, "-g", video_url
  popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
  popen.wait()
  output = popen.stdout.read()
  output = str(output).replace("b'","").replace("\\n'","")
  file_name = "/tmp/"+video_url.split("=")[1]+".m3u8"
  download_file(output,file_name)
  print os.linesep
  ffmpeg_cmd = "/usr/bin/ffmpeg -y -re -i "+file_name+" -maxrate 15M -bufsize 240M -vcodec libx264 -crf 20 -preset ultrafast -an -f flv -muxdelay 0.05 "+sys.argv[2]
  os.system(ffmpeg_cmd)
if __name__== "__main__":
  # download_youtubedl()
  if len(sys.argv) == 3:
    proccess_youtube(sys.argv[1])
  else:
    print os.linesep+"""Usege:python Main.py <youtube_url> <rtmp_destnation_server>
Exp: python Main.py https://www.youtube.com/watch?v=y7e-GC6oGhg rtmp://demo.site.com/live/stream"""