import platform
import os
import subprocess
import sys
import urllib3
import time
urllib3.disable_warnings()
from shutil import copyfile

try:
  import requests
except ImportError:
  print ("\nError: requests package is not installed pleas run: sudo python -m pip install requests\n")
  exit(1)

import zipfile
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
ffmpeg = os.path.join(bin_dir, "ffmpeg")
protocol_whitelist = " "
if get_os_info()['system'] == 'Windows':
  isWindows = True
  youtubedl = os.path.join(bin_dir,"youtube-dl.exe")
  ffmpeg = os.path.join(bin_dir, "ffmpeg.exe")
  protocol_whitelist = " -protocol_whitelist \"file,http,https,tcp,tls\" "



def check_pre_requirements(): 
  if not os.path.exists(bin_dir):
    os.makedirs(bin_dir)
  pre_requirements = { "python":True, "youtube_dl":False, "ffmpeg":False}
  if not sys.version_info[0] > 2:
    pre_requirements["python"] = False
    if not isWindows:
      if not os.path.exists(youtubedl):
        pre_requirements["youtube_dl"] = True
      if not os.path.exists("/usr/bin/ffmpeg"):
        pre_requirements["ffmpeg"] = True
      else:
        if not os.path.exists(ffmpeg):
          os.symlink("/usr/bin/ffmpeg", ffmpeg)
    else:
      if not os.path.exists(youtubedl):
        pre_requirements["youtube_dl"] = True
      if not os.path.exists(ffmpeg):
        pre_requirements["ffmpeg"] = True
    return pre_requirements
       

def download_file(url, file_name):
  # urllib.urlretrieve(url, filename, reporthook)
  #wget.download(url,filename)
  with open(file_name, "wb") as f:
    start_time =time.clock()
    print "Downloading %s" % os.path.basename(file_name)
    response = requests.get(url, allow_redirects=True, stream=True)
    total_length = response.headers.get('content-length')
    if total_length is None: # no content length header
        f.write(response.content)
    else:
        dl = 0
        float_total_lenth = float(total_length)
        int_total_length = int(total_length)
        for data in response.iter_content(chunk_size=int_total_length/100):
            dl += len(data) 
            f.write(data)
            done = int(50 * dl / int_total_length)
            sys.stdout.write("\r[%s%s] Doloaded %.3fMB out of %.3fMB @ %.3fKBs" % ('=' * done, ' ' * (50 - done),float(float(dl)/1024/1024),  float(float_total_lenth/1024/1024), float(dl  / (1024 * (time.clock() - start_time)))))    
            sys.stdout.flush()
  f.close()
  print "\ndone"
  
def download_ffmpeg():
  if not isWindows:
    print "Downloading ffmpeg with apt:"
    os.system('sudo apt install ffmpeg -y')
    os.symlink("/usr/bin/ffmpeg", ffmpeg)
  else:
    #subprocess.call(["C:\\WINDOWS\\system32\\WindowsPowerShell\\v1.0\\powershell.exe",  "Start-BitsTransfer -Source 'https://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-latest-win64-static.zip' -Destination {}".format(os.path.join(gettempdir(),"ffmpeg.zip"))])
    download_file("https://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-latest-win64-static.zip",os.path.join(gettempdir(), "ffmpeg.zip"))
    zip_ref = zipfile.ZipFile(os.path.join(gettempdir(), "ffmpeg.zip"), 'r')
    zip_ref.extractall(gettempdir())
    zip_ref.close()
    copyfile(os.path.join(gettempdir(), "ffmpeg-latest-win64-static\\bin\\ffmpeg.exe"),ffmpeg)

def download_youtubedl():
  if not isWindows:
    dlfile = os.path.join(bin_dir,"youtube-dl")
    try:
      download_file("https://yt-dl.org/downloads/latest/youtube-dl", youtubedl)
      os.chmod(youtubedl, 509)
      print os.linesep
    except Exception as e:
      os.remove(dlfile)
      raise Exception(str(e))
  else:
    try:
      print "Downloading youtube-dl.exe"
      download_file("https://yt-dl.org/downloads/latest/youtube-dl.exe", youtubedl)
      print os.linesep
    except Exception as e:
      os.remove(dlfile)
      raise Exception(str(e))

def proccess_youtube(video_url):
  print "Getting youtube stream..."
  cmd = youtubedl, "--list-formats", video_url    
  popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
  popen.wait()
  output = popen.stdout.readlines()
  print "Fatching relevant stream..."
  best = str(output[-1]).replace("b'","").split(' ')[0]
  cmd = youtubedl ,"-f", best, "-g", video_url
  popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
  popen.wait()
  output = popen.stdout.read()
  output = str(output).replace("b'","")
  output = output.replace("\n","")

  print os.linesep
  ffmpeg_cmd = "{} -hide_banner -re{}-i {} -c copy -an -bufsize 4M -crf 20 -preset ultrafast -f flv -muxdelay 0.05 {}".format(ffmpeg, protocol_whitelist, output, sys.argv[2])
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
    print os.linesep+"""Usege:python {} <youtube_url> <rtmp_destnation_server>
Exp: python {} https://www.youtube.com/watch?v=y7e-GC6oGhg rtmp://demo.site.com/live/stream""".format(os.path.basename(sys.argv[0]),os.path.basename(sys.argv[0]))
