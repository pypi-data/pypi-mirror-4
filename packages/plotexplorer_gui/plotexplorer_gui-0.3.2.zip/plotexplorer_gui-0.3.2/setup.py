from setuptools import setup

setup(name='plotexplorer_gui',
        version='0.3.2',
        description='A wxpython/matplotlib script for plotting and contrasting a collection of graphs',
        long_description="""\
        This script creates a matplotlib window next to the sortable list of checkboxes from which
        graphs can be selected. This is a quick way to compare many similar plots and explore
        such data sets. The list of available graphs can consist of several columns of metadata which 
        can each be sorted. The final graph can be saved as an image or a csv file.
        
        This script depends upon wxpython and matplotlib.
        """,
        classifiers=[
          "License :: OSI Approved :: BSD License",
          "Programming Language :: Python :: 2",
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "Intended Audience :: Science/Research",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Topic :: Scientific/Engineering :: Visualization"
           ],
        author='robochat',
        author_email='rjsteed@talk21.com',
        #url='?',
        license='BSD',
        keywords='matplotlib',
        py_modules=['plotexplorer_gui'], # this code is too small to setup a package system
        #scripts=[],
        #data_files=[('',[,'README'])],
        install_requires=['matplotlib','wxpython','numpy'],
        zip_safe=False
        )


