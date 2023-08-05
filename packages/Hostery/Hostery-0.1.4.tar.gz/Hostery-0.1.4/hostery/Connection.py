import ftplib
import tempfile
import getpass
import shutil
import os

from git import ignore
from utils import *
 
class Connection():

  @staticmethod
  def FromConfig(config):
    return Connection.ByType[config['type']](config)
  
  def __init__(self, config):
    self.config = config

  def stage(self, *upload_items):

    staging_directory = self.get_staging_directory()
    supports_symlinks = self.supports_symlinks()

    for item in upload_items:

      base = os.path.join(staging_directory, item.dest)
      command('mkdir -p %s'%base, verbose=False) 

      if supports_symlinks and item.symlink:
        make_symlink(staging_directory, item.path, item.dest, item.symlink)
      else:
        command('cp -a %s %s'%(item.path, base), verbose=False)     

      loc = os.path.join(base, os.path.split(item.path)[1])
      command('chmod 744 %s'%loc, verbose=False) # this became necessary all of a sudden? (for rsync)

      if item.rename:
        new = os.path.join(os.path.abspath(base), item.rename)
        command('mv %s %s'%(loc, new), verbose=False)

  def supports_symlinks(self):
    return False
  def supports_partial_upload(self):
    return True
  def connect(self):
    pass
  def disconnect(self):
    pass

def make_symlink(base, path, dest, symlink):

  split = os.path.split(path)
  filename = split[1]
  
  fro = os.path.join(dest, filename)
  to = os.path.join(symlink, path)

  relpath = os.path.relpath(to, dest)

  command('ln -s %s %s'%(relpath, os.path.join(base, fro)), verbose=False)

class RsyncConnection(Connection):

  @staticmethod
  def GetConfig():
    print 'Enter empty host/user strings for local destinations'
    return {
      'type': 'rsync',
      'host': raw_input('Host: '),
      'login': raw_input('User: '),
      'root': raw_input('Root: ')
     }

  def __init__(self, config):
    Connection.__init__(self, config)
    if config['host']:
      self.__dest = '%s@%s:~/%s'%(config['login'], config['host'], config['root'])
    else:
      self.__dest = config['root']
    self.__staging_directory = tempfile.mkdtemp()

  def get_staging_directory(self):
    return self.__staging_directory

  def disconnect(self):
    shutil.rmtree(self.__staging_directory)

  def upload(self):
    command('rsync -lrz %s/ %s'%(self.__staging_directory, self.__dest), verbose=True)

  def supports_symlinks(self):
    return True


class GAEConnection(Connection):

  StagingDirectory = 'hostery-files'

  @staticmethod
  def GetConfig():
    ignore(GAEConnection.StagingDirectory)
    return { 'type': 'gae', 'root': GAEConnection.StagingDirectory }

  def get_staging_directory(self):
    return GAEConnection.StagingDirectory

  def supports_partial_upload(self):
    return False

  def supports_symlinks(self):
    return True

  def upload(self):
    command('appcfg.py update .', verbose=True)


class FTPConnection(Connection):

  @staticmethod
  def GetConfig():
    return {
      'type': 'ftp',
      'host': raw_input('Host: '),
      'root': raw_input('Root: '),
      'login': raw_input('User: '),
      'port': int(raw_input('Port: '))
    }

  def __init__(self, config):
    Connection.__init__(self, config)
    self.__split_root = ['/']+config['root'].split(os.sep)
    self.__upload_list = []

  def get_staging_directory(self):
    return '.'

  def stage(self, *upload_items):
    self.__upload_list = self.__upload_list + upload_items

  def connect(self):
    print 'Logging in to %s as %s...'%(self.config['host'], self.config['login'])
    self.ftp = ftplib.FTP()
    self.ftp.connect(self.config['host'], self.config['port'])
    print self.ftp.getwelcome()
    self.ftp.login(self.config['login'], getpass.getpass('Password: '))

  def disconnect(self):
    print 'Logging out...'
    self.ftp.quit()

  def upload(self):

    for u in self.__upload_list:
      self.__cwd(*u.dest.split(os.sep))
      
      if u.rename:
        self.__upload(u.path, u.rename)
      else:
        self.__upload(u.path)

      self.__cwd_root()

  def __cwd_root(self):
    self.__cwd(*self.__split_root)

  def __cwd(self, *args):
    for d in args:
      try:
        self.ftp.cwd(d)
      except:
        self.ftp.mkd(d)
        self.ftp.cwd(d)

  def __upload(self, fullname, name=None):
    if not name:
      name = os.path.split(fullname)[1]
    with open(fullname, 'rb') as f:
      self.ftp.storbinary('STOR ' + name, f)
      f.close()
    print 'Uploaded ', fullname


Connection.ByType = dict(rsync=RsyncConnection, gae=GAEConnection, ftp=FTPConnection)