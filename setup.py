from setuptools import setup

def readme():
      with open('README.md', 'r') as f:
            return f.read()

meta = {
      'name': 'xinpu',
      'version': '0.1.0',
      'description': 'Publish news from RSS feeds to Plurk',
      'long_description': readme(),
      'url': 'https://github.com/rschiang/xinpu',
      'author': 'Poren Chiang',
      'author_email': 'ren.chiang@gmail.com',
      'license': 'BSD',
      'packages': ['xinpu'],
      'scripts': ['bin/xinpu'],
      'install_requires': ['feedparser', 'python-dateutil', 'beautifulsoup4'],
      'dependency_links': ['https://github.com/clsung/plurk-oauth.git#egg=plurk_oauth'],
      'include_package_data': True,
      'zip_safe': False,
}

setup(**meta)
