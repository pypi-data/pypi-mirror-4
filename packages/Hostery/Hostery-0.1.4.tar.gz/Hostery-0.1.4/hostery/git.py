import os
import traceback

from utils import *

def is_controlled():
  return os.path.isdir('.git')

def is_dirty():
  return '*' == command('[[ $(git diff --shortstat 2> /dev/null | tail -n1) != "" ]] && echo "*"')

def has_untracked():
  return 0 < len(command('git ls-files . --exclude-standard --others'))

def controlled_files():
  return command('git ls-tree -r master | cut -f2', multiline=True)

def remote_tags():
  return command('git ls-remote --tags --quiet', multiline=True)

def ignore(pattern):
  command('touch .gitignore')
  with open('.gitignore', 'r') as f:
    ignored = f.read().split('\n')
  if not pattern in ignored:
    with open('.gitignore', 'a') as f:
      f.write('\n'+pattern)

def commit_number():
  line = command('git rev-parse --verify HEAD')[:7]
  if line == 'fatal: Needed a single revision':
    return False
  return line

def branch_name():
  return command('git branch | grep "*" | sed "s/* //"')

def changed_files(commit, prev):
  cmd = 'git diff --name-only %s %s'%(commit, prev)
  if command(cmd, return_success=True):
    return command(cmd, multiline=True)
  else:
    return False

def has_origin():  
  return 'origin' in command('git remote', multiline=True)

def add(path):
  command('git add %s'%path, verbose=True)

def checkout_empty_branch(name):
  command('git symbolic-ref HEAD refs/heads/%s'%name)

def stash():
  return command('git stash', verbose=True) != 'No local changes to save'

def stash_pop():
  command('git stash pop', verbose=True)

def checkout(target):
  command('git checkout %s'%target, verbose=True)

def commit(message):
  command('git commit -m "%s"'%message, verbose=True)

def push(branch):
  if not has_origin():
    print_color('Repository has no origin.', colors.WARNING)
  else:
    command('git push origin %s'%branch, verbose=True)

def pull(branch):
  if not has_origin():
    print_color('Repository has no origin.', colors.WARNING)
  else:
    command('git pull origin %s'%branch, verbose=True)

def safe_checkout(target, txn, empty_branch=False):

  # todo: skip if we're already at target.

  og_branch = branch_name()
  stashed = stash()

  def restore():
    checkout(og_branch)
    if stashed:
      stash_pop()

  try:
    
    if empty_branch:
      checkout_empty_branch(target)
    else:
      checkout(target)
    to_return = txn(target)

  except :
    print_color('Caught exception during git checkout.', colors.WARNING)
    print traceback.format_exc()
    restore()
    quit()

  restore()

  return to_return