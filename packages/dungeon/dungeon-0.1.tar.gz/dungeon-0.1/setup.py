try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    
config = {
    'description' : 'Dungeon of Crow',
    'author' : 'Nicolas tarral',
    'url' : 'just local',
    'download_url' : 'local',
    'author_email' : 'nicolas@tarral.net',
    'version' : '0.1',
    'install_requires' : ['nose'],
    'packages' : ['dungeon'],
    'scripts' : ['bin/testprint.py'],
    'name' : 'dungeon'
}
 
setup(**config)
