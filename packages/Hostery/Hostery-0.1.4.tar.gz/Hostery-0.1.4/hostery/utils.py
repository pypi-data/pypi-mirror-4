import os
import subprocess 

class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def print_color(msg, color):
  print color + msg + colors.ENDC

def command(cmd, verbose=False, return_success=False, multiline=False, dry=False):
  
  if verbose or dry:
    print_color(cmd, colors.OKBLUE)

  if dry:
    return

  if multiline:
    
    cmd = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    s = []
    for line in cmd.stdout:
      line = line.strip()
      if line != '':
        s.append(line) 
  else:
    p = os.popen(cmd)
    s = p.readline().strip()

  if s and verbose:
    if multiline:
      for l in s:
        print l
    else:
      s = s.strip()
      if s.startswith('fatal'):
        print_color(s, colors.FAIL)
      else:
        print s

  if return_success:
    return p.close() == None
  return s