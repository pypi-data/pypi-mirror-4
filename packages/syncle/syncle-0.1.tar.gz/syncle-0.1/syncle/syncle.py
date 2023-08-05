#!/usr/bin/env python

import sys, os, shutil, time, yaml

config_path = os.path.expanduser("~/.synclerc.yml")
src_paths = []
targets_dir = ""
delay = 3

def get_settings():
  global src_paths, targets_dir, delay
  if not os.path.exists(config_path):
    f = open(config_path, "w")
    if f:
      f.close()
      print "Syncle configuration file %s was created" % config_path
    else:
      sys.exit("Syncle can not create configuration file")
  config = yaml.load(open(config_path))
  if config:
    if 'files' in config:
      src_paths = config['files']
    if 'storage' in config:
      targets_dir = config['storage']
    if 'delay' in config:
      delay = config['delay']

def main():
  global src_paths, targets_dir, delay
  while True:
    get_settings()
    for src_path in src_paths:
      src_path = os.path.expanduser(src_path)
      targets_dir = os.path.expanduser(targets_dir)

      target_path = os.path.join(targets_dir, os.path.split(src_path)[-1])

      src_mtime = os.stat(src_path).st_mtime
      target_mtime = 0
      if os.path.exists(target_path):
        target_mtime = os.stat(target_path).st_mtime

      if src_mtime > target_mtime:
        shutil.copy2(src_path, target_path)
      elif src_mtime < target_mtime:
        shutil.copy2(target_path, src_path)

    time.sleep(delay)
