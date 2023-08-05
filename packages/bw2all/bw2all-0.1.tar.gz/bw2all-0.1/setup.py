from distutils.core import setup

setup(
  name='bw2all',
  version="0.1",
  packages=["bw2all"],
  author="Chris Mutel",
  author_email="cmutel@gmail.com",
  license=open('LICENSE.txt').read(),
  requires=["brightway2", "bw2calc", "bw2ui", "bw2analyzer", "numpy",
    "progressbar", "flask", "nose", "docopt", "voluptuous", "scipy"],
  url="https://bitbucket.org/cmutel/brightway2-all",
  long_description=open('README').read(),
)
