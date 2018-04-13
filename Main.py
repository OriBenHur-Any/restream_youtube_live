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


#Golbal vars
bin_dir = os.path.join(os.getcwd(),"bin")
isWindows = False
youtubedl = os.path.join(bin_dir,"youtube-dl")
if get_os_info()['system'] == 'Windows':
  isWindows = True
  youtubedl = os.path.join(bin_dir,"youtube-dl.exe")



def check_pre_requirements(): 
  if not os.path.exists(bin_dir):
    os.makedirs(bin_dir)
  pre_requirements = { "python":True, "youtube_dl":False, "ffmpeg":False}
  if not sys.version_info[0] > 2:
    pre_requirements["python"] = False
    if not isWindows:
      if not os.path.exists(os.path.join(bin_dir, "youtube-dl")):
        pre_requirements["youtube_dl"] = True
      if not os.path.exists("/usr/bin/ffmpeg"):
        pre_requirements["ffmpeg"] = True
      else:
        if not os.path.exists(os.path.join(format(bin_dir),'ffmpeg')):
          os.symlink("/usr/bin/ffmpeg",  os.path.join(bin_dir,"ffmpeg"))
          # os.system('ln -s {} {}'.format("/usr/bin/ffmpeg", os.path.join(bin_dir,"ffmpeg")))
    else:
      if not os.path.exists(os.path.join(bin_dir, "youtube-dl.exe")):
        pre_requirements["youtube_dl"] = True
      if not os.path.exists(os.path.join(bin_dir, "ffmpeg.exe")):
        pre_requirements["ffmpeg"] = True
    return pre_requirements
       
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

def download_ffmpeg():
  if not isWindows:
    os.system('sudo apt install ffmpeg')
  else:
    download_file("https://storage.cloud.google.com/anyvision-images/ffmpeg.exe",os.path.join(bin_dir, "ffmpeg.exe"))


def download_youtubedl():
  if not isWindows:
    dlfile = os.path.join(bin_dir,"youtube-dl")
    try:
      print "Downloading youtube-dl"
      download_file("https://yt-dl.org/downloads/latest/youtube-dl", dlfile)
      print os.linesep
    except Exception as e:
      os.remove(dlfile)
      raise Exception(str(e))
  else:
    dlfile = os.path.join(bin_dir,"youtube-dl.exe")
    try:
      print "Downloading youtube-dl.exe"
      download_file("https://yt-dl.org/downloads/latest/youtube-dl.exe", dlfile)
      print os.linesep
    except Exception as e:
      os.remove(dlfile)
      raise Exception(str(e))

def proccess_youtube(video_url):
  cmd = youtubedl, "--list-formats", video_url
  if not isWindows:
    os.chmod(youtubedl, 509)
  print "Getting youtube stream..."
  popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
  popen.wait()
  output = popen.stdout.readlines()
  best = str(output[-1]).replace("b'","").split(' ')[0]
  cmd = youtubedl ,"-f", best, "-g", video_url
  popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
  popen.wait()
  output = popen.stdout.read()
  output = str(output).replace("b'","").replace("\\n'","")
  file_name = "{}.m3u8".format(os.path.join(gettempdir(),video_url.split("=")[1]))
  download_file(output,file_name)
  print os.linesep

  if not isWindows:
    ffmpeg = os.path.join(bin_dir, "ffmpeg")
  else:
    ffmpeg = os.path.join(bin_dir, "ffmpeg.exe")

  ffmpeg_cmd = "{} -y -re -i {} -maxrate 15M -bufsize 240M -vcodec libx264 -crf 20 -preset ultrafast -an -f flv -muxdelay 0.05 {}".format(ffmpeg, file_name, sys.argv[2])
  os.system(ffmpeg_cmd)


if __name__== "__main__":
  if len(sys.argv) == 3:
    pre_requirements = check_pre_requirements()
    if pre_requirements["python"]:
      raise Exception("Python 2 version is required.")
    if pre_requirements["youtube_dl"]:
       download_youtubedl()
    if pre_requirements["ffmpeg"]:
      download_ffmpeg()
    
    proccess_youtube(sys.argv[1])
  else:
    print os.linesep+"""Usege:python Main.py <youtube_url> <rtmp_destnation_server>
Exp: python Main.py https://www.youtube.com/watch?v=y7e-GC6oGhg rtmp://demo.site.com/live/stream"""