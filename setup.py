from setuptools import setup

setup(name='xinpu',
      version='0.1.0',
      description='Publish news from RSS feeds to Plurk',
      url='https://github.com/rschiang/xinpu',
      author='Poren Chiang',
      author_email='ren.chiang@gmail.com',
      license='BSD',
      packages=['xinpu'],
      install_requires=[
            'feedparser',
            'python-dateutil',
            'beautifulsoup4',
      ],
      dependency_links=[
            'git+https://github.com/clsung/plurk-oauth.git#egg=plurk_oauth',
      ],
      zip_safe=False)
