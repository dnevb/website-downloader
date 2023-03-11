import os
import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup as BS

import utils

dir = 'output'

def run(url):
  print('page download started')
  os.makedirs(dir, exist_ok=True)
  try:
    subprocess.run(
      f'wget {url} --header "user-agent: me" -r -l 1 -np -nH -k -m -P output --no-clobber --html-extension',
      text = True,
      shell = True
    )
  except KeyboardInterrupt:
    pass
  print('page download finished')
  translate_files('output', 'res')

def translate_files(dir, out):
  items = Path(dir).iterdir()
  os.makedirs(out, exist_ok=True)
  files = []
  dirs = []

  for item in items:
    if item.is_dir(): dirs.append(item)
    if item.is_file(): files.append(item)

  dirs.sort(key=lambda x: len(x.as_posix()))
  files.sort(key=lambda x: len(x.as_posix()))

  for item in files:
    path = item.as_posix().replace(dir, out)
    f = item.read_bytes()

    with open(path, 'wb') as b:
      try:
        text = f.decode('utf-8')
        if not 'html' in text.split('\n')[0]:
          b.write(f)
          continue

        t = utils.translate_html(text, item.name)
        b.write(t.encode('utf-8'))
      except UnicodeDecodeError:
        b.write(f)

  for item in dirs:
    path = item.as_posix().replace(dir, out)
    translate_files(item.as_posix(), path)

if __name__ == "__main__":
  urls = sys.argv[1:]
  run(' '.join(urls))