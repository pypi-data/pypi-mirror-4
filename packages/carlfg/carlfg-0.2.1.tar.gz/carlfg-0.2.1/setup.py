from setuptools import setup

setup(name='carlfg',
      version='0.2.1',
      description='find CG coefficients, find the sum of all natural numbers from 1 to n',
      url='https://github.com/psachin/carlfg',
      author='sachin',
      author_email='isachin@iitb.ac.in',
      license=open('LICENSE.rst').read(),
      packages=['cg'],
      scripts=['bin/cg','bin/clebg'],
      long_description=open('README.rst').read(),
      keywords=['cg','clebg','pypi','coefficients','clebsch gordan'],
      install_requires=["python-wxgtk2.8",
                        "python-wxtools",
                        "wx-2.8-i18n"
                        ],
      zip_safe=False)
