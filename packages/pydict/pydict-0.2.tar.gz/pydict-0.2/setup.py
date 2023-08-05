from setuptools import setup

def readme():
		with open('README.rst') as f:
				return f.read()

setup(name='pydict',
      version='0.2',
      description='Command line dictionary',
      url='http://github.com/sagarrakshe/pydict',
      author='Sagar Rakshe',
      author_email='sagarrakshe2@gmail.com',
      license='GPL',
      packages=['pydict'],
	  scripts=['bin/pydict'],
	  install_requires=['mechanize','BeautifulSoup'],
      zip_safe=False)
