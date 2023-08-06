from distutils.core import setup

setup(
    name='ImageSlicer',
    version='0.1.01',
    author='Jake Zerrer',
    author_email='him@jakezerrer.com',
    packages=['imageslicer'],
    url='http://pypi.python.org/pypi/ImageSlicer/',
    license='LICENSE.txt',
    description='Slice an image into rectangles sutable for tiled printing.',
    long_description=open('README.txt').read(),
    install_requires=[
        "PIL >= 1.1.6",
    ],
)