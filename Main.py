import platform
import os
import urllib.request
import sys
import subprocess
from tempfile import gettempdir

def linux_distribution():
  try:
    return platform.linux_distribution()
  except:
    return "N/A"

def download_file(url, outfile):
  urllib.request.urlretrieve(url, outfile)
  

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

if sys.version_info[0] < 3:
  raise Exception("Python 3 or a more recent version is required.")

def download_youtubedl():
  if get_os_info()['system'] != 'Windows':
    try:
      download_file("https://yt-dl.org/downloads/latest/youtube-dl", "/tmp/youtube-dl")
      return str("/tmp/youtube-dl"), True 
    except Exception as e:
      raise Exception(str(e))
  else:
    try:
      download_file("https://yt-dl.org/downloads/latest/youtube-dl", os.path.join(gettempdir(),"youtube-dl"))
      return str(os.path.join(gettempdir(),"youtube-dl")), False 
    except Exception as e:
      raise Exception(str(e))

def proccess_youtube(video_url):
  binfile = download_youtubedl()
  cmd = binfile[0], "--list-formats", video_url
  if binfile[1]:
    os.chmod(binfile[0], 0o775)
  popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
  popen.wait()
  output = popen.stdout.readlines()
  best = str(output[-1]).replace("b'","").split(' ')[0]
  cmd = binfile[0] ,"-f", best, "-g", video_url
  popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
  popen.wait()
  output = popen.stdout.read()
  output = str(output).replace("b'","").replace("\\n'","")
  # print(best)
  # line = popen.stdout.readline
  # while popen.stdout.readline() != "b''":
  #   print(str(popen.stdout.readline()).replace("\n'",'').replace("b'",''))
  # output = popen.stdout.
  # print (output)
  download_file(output,"/tmp/file.m3u8")
  ffmpeg_cmd = "/usr/bin/ffmpeg -y -re -i /tmp/file.m3u8 -maxrate 15M -bufsize 1000M -vcodec libx264 -crf 20 -preset ultrafast -an -f flv -muxdelay 0.05 rtmp://demo3.anyvision.co/live/stream"
  os.system(ffmpeg_cmd)
if __name__== "__main__":
  # download_youtubedl()
  proccess_youtube("https://www.youtube.com/watch?v=y7e-GC6oGhg")