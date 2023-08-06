from distutils.core import setup

execfile('version.py')

setup(name="dipole_error",
      version=__version__,
      description="Calculate the predicted dipole value and error for given input.",
      py_modules=['dipole_error'],
      author='Jonathan Whitmore',
      author_email='jbwhit@gmail.com',
      url='https://github.com/jbwhit/dipole_error',
      requires = ["angles", "uncertainties"],
      )
      # download_url
      # long_description
      # classifiers?
      # install_requires = ["angles", "uncertainties"],
      