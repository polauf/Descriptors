from setuptools import setup

setup(name='descriptors',
      version='0.1',
      description='Fork to IPythons traitlets',
      longdescription='''Programed it 2 year ago. It have some nice possibilites like shared value between instances and callbackable Sequences etc... Enjoy
TODO:
- Comaptible api with traitlets
- separate callbacks from sequences (it is a mess)
-
      '''
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Build Tools',
        ],
#      url='http://github.com/TODO',
      author='Matouš Polauf',
#      author_email='polauf@NOTHING',
      license='MIT',
      packages=['descriptors'],
      zip_safe=False)
