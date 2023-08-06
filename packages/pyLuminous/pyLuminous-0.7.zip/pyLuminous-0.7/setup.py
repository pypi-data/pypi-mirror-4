from setuptools import setup

setup(name='pyLuminous',
        version='0.7',
        description='Optical Transfer Matrix and simple Quantum Well modelling',
        long_description="""\
        This library consists of two sublibraries pyFresnel and pyQW for performing
        physics simulations. pyFresnel contains codes for modelling the optical 
        properties of dielectric layers, starting from a simple interface and
        finishing with an optical transfer matrix code. Unlike other optical 
        transfer matrix codes, this code allows for layers with uniaxial dielectrics
        which have their the optical axes normal to the plane of the layers.
        
        pyQW is a code for a semi-analytical simulation of a finite semiconductor
        quantum well (conduction band). It also models the well's intersubband
        transitions (transitions between the conduction band levels).
                
        This library depends upon numpy, scipy and matplotlib.
        """,
        classifiers=[
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
          "Programming Language :: Python :: 2",
          "Development Status :: 4 - Beta",
          "Intended Audience :: Science/Research",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Topic :: Scientific/Engineering :: Physics",
          "Topic :: Scientific/Engineering"
           ],
        author='robochat',
        author_email='rjsteed@talk21.com',
        url='https://sourceforge.net/projects/pyluminous/',
        license='GPLv3',
        keywords='optics optical transfer matrix quantum light',
        packages=['pyFresnel','pyQW'],
        #package_data={'pyQW'  :['COPYING','QW_modelling_RSteed_2013.pdf']},
        #py_modules=['plotexplorer_gui'], # this code is too small to setup a package system
        #scripts=[],
        #data_files=[('',[,'README'])],
        install_requires=['numpy','matplotlib','scipy'],
        zip_safe=False
        )


