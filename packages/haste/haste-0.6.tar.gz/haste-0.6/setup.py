from setuptools import setup

setup(name="haste",
      version="0.6",
      author="Devon Meunier",
      author_email="devon.meunier@utoronto.ca",
      url="http://www.cdf.utoronto.ca/~g8m/",
      license="MIT",
      py_modules=['haste'],
      entry_points={
          "console_scripts": [
              "haste = haste:main",
              ],
      },
      description="Pure Python replacement of the hastebin.com client.",
      install_requires=[
          "requests",
          "docopt>=0.3.0",
      ],
)
