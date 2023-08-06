from setuptools import setup, find_packages

version = '1.14'

setup(name='hmako',
      version=version,
      description="a hack version mako(0.74) for html , will remove empty line",
      keywords='wsgi myghty mako',
      author='zsp',
      author_email='zsp007@gmail.com',
      license='MIT',
      packages = ["hmako","hmako.ext"],
      zip_safe=False
)
