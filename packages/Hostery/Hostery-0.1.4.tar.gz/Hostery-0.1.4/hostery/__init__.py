#!/usr/bin/env python
import os
import sys
import json
import tempfile
import shutil
import time

from datetime import datetime
from jinja2 import Template

import git

from Connection import Connection
from utils import *

HOSTERY_CONFIG = '.hostery-config'
HOSTERY_BRANCH = 'hostery'
HOSTERY_FILE = '.hostery'
HOSTERY_DIR = os.path.dirname(os.path.realpath(__file__))

EXCLUDE_FILES = ['.gitignore']
INDEX_TEMPLATE = os.path.join(HOSTERY_DIR, 'iframe.tmpl')

DIR = os.getcwd()

class UploadItem():
  def __init__(self, path, prefix_dir=None, rename=None, symlink=False):
    self.path = path
    self.dest = os.path.join(prefix_dir, os.path.split(path)[0]) if prefix_dir else ''
    self.rename = rename
    self.symlink = symlink


def init(args):
  
  if not git.is_controlled():
    print_color('fatal: Not a git repository', colors.FAIL)
    quit()
  
  if os.path.isfile(HOSTERY_CONFIG):
    print_color('fatal: Hostery already configured. Edit or delete %s'% HOSTERY_CONFIG, colors.FAIL)
    quit()
  
  # instantiate hostery config

  hostery_config = open(HOSTERY_CONFIG, 'w')
  
  data = Connection.ByType[args.type].GetConfig()
  hostery_config.write(json.dumps(data, indent=2))
  hostery_config.close()
  
  git.ignore(HOSTERY_CONFIG)

  # make empty hostery file on empty hostery branch    
  def txn(branch):
    
    # git ignore everything except hostery file and gitignore.
    command('git rm --cached . -r', verbose=True)
    git_ignore = open('.gitignore', 'w')
    git_ignore.write('*\n!.gitignore\n!%s'%HOSTERY_FILE)
    git_ignore.close()
    git.add('.gitignore')

    # make hostery file
    hostery_file = open(HOSTERY_FILE, 'w')
    hostery_file.write(json.dumps({}))
    hostery_file.close()

    # add, commit, push.
    git.add(HOSTERY_FILE)
    command('git status', multiline=True, verbose=True)
    git.commit('hostery init')
    git.push(branch)

  git.safe_checkout(HOSTERY_BRANCH, txn, empty_branch=True)

  print 'Hostery configured! Use "hostery mark" to upload a commit.'


def mark(args):

  if not os.path.isfile(HOSTERY_CONFIG):
    print_color('fatal: Not a configured for hostery. Use "hostery init".', colors.FAIL)
    quit()

  #read hostery file
  hostery_config = open(HOSTERY_CONFIG, 'rb')
  config = json.loads(hostery_config.read())
  hostery_config.close()

  # check if has single revision
  commit_number = git.commit_number()
  if not commit_number:
    quit()

  # do git sync
  if args.skip_git:
    print_color('Skipping git sync.', colors.WARNING) 
  else: 
    git_sync()

  commits_to_copy = [i[:7] for i in (args.commits or [commit_number])]

  # get/update commit data
  print_color('Updating hostery data ...', colors.HEADER)

  # todo
  commit_data = update_hostery_file(commits_to_copy)

  #read hostery config, instantiate connection
  hostery_config = open(HOSTERY_CONFIG, 'rb')
  config = json.loads(hostery_config.read())
  hostery_config.close()

  # start connection
  connection = Connection.FromConfig(config)
  connection.connect()

  # update index.html
  temp_index_file = update_index_file(commit_data)

  if not connection.supports_partial_upload():
    # see what's not in the staging dir that *is* in the hostery file
    # add those to the list.
    for (_, dirs, _) in os.walk(connection.get_staging_directory()):
      commits_to_copy += filter(lambda c: c not in dirs, commit_data.keys())
      commits_to_copy = list(set(commits_to_copy))
      break

  def copy_commit(commit):
    upload_list = get_upload_list(commit, commit_data, not args.skip_symlinks)
    print_color('Staging files for %s ...'%commit, colors.HEADER)  
    print_upload_list(upload_list, config['root'])
    connection.stage(*upload_list)

  # stage commits
  print_color('Staging files for %s ...'%', '.join(commits_to_copy), colors.HEADER)
  
  for commit in commits_to_copy:
    git.safe_checkout(commit, copy_commit)

  # add index.html to upload list at root
  connection.stage(UploadItem(temp_index_file.name, rename='index.html'))

  # upload files
  if not args.skip_upload:
    print_color('Uploading files ...', colors.HEADER)
    connection.upload()

  # end connection
  connection.disconnect()

  # clean up
  temp_index_file.close()

  print_color('Done.', colors.HEADER)


def destroy(args):
  command('rm %s'%HOSTERY_CONFIG, verbose=True)
  command('git branch -D %s'%HOSTERY_BRANCH, verbose=True)
  command('git push origin --delete %s'%HOSTERY_BRANCH, verbose=True)


def git_sync():
  
  branch_name = git.branch_name()

  if git.is_dirty():
    print_color('fatal: Can\'t publish a dirty directory.', colors.FAIL)
    quit()

  if git.has_untracked():
    print_color('fatal: There are untracked files.', colors.FAIL)
    quit()

  git.pull(branch_name)

  if git.is_dirty():
    print_color('Fix merge conflicts.', colors.FAIL)
    quit()

  git.push(branch_name)


def update_hostery_file(commits):
  
  data = {}

  def write_txn(branch):

    git.pull(branch)

    hostery_file = open(HOSTERY_FILE, 'r')
    all_data = json.loads(hostery_file.read())
    print all_data
    all_data.update(data)
    hostery_file.close()

    hostery_file = open(HOSTERY_FILE, 'w')
    hostery_file.write(json.dumps(all_data, indent=2))
    hostery_file.close()

    git.add(HOSTERY_FILE)

    # command('git status', verbose=True)

    git.commit('hostery mark')

    git.push(branch)

    return all_data

  for commit in commits:
    data[commit] = get_commit_data(commit)

  
  # get info from each commit, add it to data
  return git.safe_checkout(HOSTERY_BRANCH, write_txn)
  # go back 

def update_index_file(commit_data):

  commit_data = sorted(commit_data.values(),
    key=lambda commit: commit['date'],
    reverse=True)

  def convert_date(commit):
    commit['date'] = datetime.fromtimestamp(commit['date'])

  map(convert_date, commit_data)

  template_file = open(INDEX_TEMPLATE, 'r')
  template = Template(template_file.read())
  html = template.render(commit_data=commit_data, repo_name=os.path.basename(DIR))
  template_file.close()

  temp = tempfile.NamedTemporaryFile(mode='w+t')
  temp.write(html)
  temp.seek(0)
  return temp


def get_upload_list(commit_number, commit_data, symlink):
  
  files = get_controlled_files()
  
  if len(files) == 0:
    print_color('No files to upload.', colors.FAIL)
    return []

  def make_upload_item(path):
    return UploadItem(path, prefix_dir=commit_number)
  
  upload_list = map(make_upload_item, files)

  prev_commit = get_previous_commit(commit_number, commit_data)

  if not prev_commit or not symlink:
    return upload_list
  
  print_color('Previous marked commit is %s%s'%(colors.OKBLUE, prev_commit), colors.HEADER)
  
  changed_files = git.changed_files(commit_number, prev_commit)
  
  if changed_files == False:
    print_color('Skipping symlink step. Could not read changed files.', colors.WARNING)
    return
  
  def symlink_filter(upload_item):
    if upload_item.path not in changed_files:
      upload_item.symlink = prev_commit
    return upload_item
  
  return map(symlink_filter, upload_list)


def get_controlled_files():
  r = []
  for f in git.controlled_files():
    if f in EXCLUDE_FILES:
      continue
    r.append(f)
  return r

def get_previous_commit(commit_number, commit_data):
  commit = commit_data[commit_number]
  # assumes ascending commit dates
  for key, value in reversed(list(commit_data.iteritems())):
    if value['date'] < commit['date']:
      return key
  return None

def get_commit_data(commit):
  return {
    'date': int(time.time()), #todo read actual commit time
    'commit': commit
  }


def print_upload_list(upload_list, root):

  # get column width
  col = len(max(map(lambda x:x.path, upload_list), key=len))

  for item in upload_list:

    if item.symlink:
      color = ''
      name = item.path
      dest = os.path.join(colors.OKBLUE + item.symlink + colors.ENDC, name)

    else:
      color = colors.OKGREEN
      name = item.path
      dest = item.dest

    print '{color}{name:{col}} -> {root}{sep}{dest}{end}'\
      .format(name=name, dest=dest, sep=os.sep, root=root, col=col, color=color, end=colors.ENDC)