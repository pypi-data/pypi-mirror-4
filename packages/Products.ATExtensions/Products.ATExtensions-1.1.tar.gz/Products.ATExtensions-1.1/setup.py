from setuptools import setup, find_packages

version = '1.1'

setup(name='Products.ATExtensions',
      version=version,
      description="This package provides some further fields and widgets for Archetypes.",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Raphael Ritz',
      author_email='raphael.ritz@gmail.com',
      url='http://pypi.python.org/pypi/Products.ATExtensions',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      )
