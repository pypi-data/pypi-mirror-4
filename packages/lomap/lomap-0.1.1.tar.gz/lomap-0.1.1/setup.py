from distutils.core import setup

setup(
	name='lomap',
	version='0.1.1',
  description='LTL Optimal Multi-Agent Planner',
  author='Alphan Ulusoy',
  author_email='alphan@bu.edu',
  url='http://hyness.bu.edu/lomap',
	packages=['lomap', 'lomap.algorithms', 'lomap.classes'],
  package_dir={'lomap': 'lomap'},
  package_data={'lomap': ['binaries/linux/*','binaries/mac/*']},
	license='MIT License',
	long_description=open('README.txt').read(),
	requires=['networkx(>=1.6)','pp(>=1.6.2)'],
)
