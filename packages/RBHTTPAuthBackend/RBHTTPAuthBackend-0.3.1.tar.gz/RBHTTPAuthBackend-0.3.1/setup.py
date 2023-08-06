from setuptools import setup, find_packages

setup(name='RBHTTPAuthBackend',
     version = "0.3.1",
     author = "Ali-Akber Saifee",
     author_email = "ali@indydevs.org",
     description = "reviewboard http auth module",
     long_description = open("README").read(),
     packages = find_packages(exclude=['ez_setup']),
     include_package_data = True,
     zip_safe = False,
     entry_points={
          'reviewboard.auth_backends': [
              'RBHTTPAuthBackend = RBHTTPAuthBackend:RBHTTPAuthBackend'
          ],
      }
)
