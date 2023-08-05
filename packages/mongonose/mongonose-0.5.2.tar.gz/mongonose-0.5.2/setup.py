from setuptools import setup, find_packages

setup(name='mongonose',
      version="0.5.2",
      classifiers=[
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP'],
      author='Kapil Thangavelu',
      author_email='kapil.foss@gmail.com',
      description="Nose plugin for automating mongodb for tests runs.",
      long_description=open("README.txt").read(),
      url='http://pypi.python.org/pypi/mongonose',
      license='BSD-derived',
      packages=find_packages(),
      install_requires=["nose"],
      include_package_data=True,
      zip_safe=True,
      entry_points="""\
      [nose.plugins.0.10]
      mongodb = mongonose:MongoDBPlugin
      """
      )
