import snake_skin
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

requirements = [r for r in map(str.strip, open('requirements.txt').readlines())]

def split_path(path, result=None):
  result = result or []
  head, tail = os.path.split(path)

  if head == '':
    return [tail] + result
  elif head == path:
    return result
  else:
    return split_path(head, [tail] + result)

def get_packages():
  packages = []
  root_dir = os.path.dirname(__file__)
  if root_dir != '':
    os.chdir(root_dir)

  for dirpath, dirnames, filenames in os.walk('snake_skin'):
    for i, dirname in enumerate(dirnames):
      if dirname.startswith('.') or dirname == '__pycache__':
        del dirnames[i]
      if '__init__.py' in filenames:
        packages.append('.'.join(split_path(dirpath)))

  return packages

setup(
  name = 'SnakeSkin',
  version = snake_skin.__version__,
  url = 'http://github.com/cadwallion/snake_skin',
  author = 'Andrew Nordman',
  author_email = 'cadwallion@gmail.com',
  description = 'Python library skeleton tool',
  packages = get_packages(),
  scripts = ['bin/snake_skin'],
  install_requires = requirements,
  classifiers = [
    'Programming Language :: Python',    
    'Programming Language :: Python :: 2.7',
    'License :: OSI Approved :: MIT License',
    'Topic :: Software Development',
    'Topic :: Software Development :: Code Generators',
    'Topic :: Utilities'
  ]
)
