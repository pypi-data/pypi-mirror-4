from distutils.core import setup

setup(name="dipole_error",
      version="1.0.25",
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
      