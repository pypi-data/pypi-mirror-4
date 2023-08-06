from distutils.core import setup

setup(
    name='ImageSlicer',
    version='0.1.03',
    author='Jake Zerrer',
    author_email='him@jakezerrer.com',
    py_modules=['imageslicer'],
    packages=['imageslicer'],
    url='http://pypi.python.org/pypi/ImageSlicer/',
    license='LICENSE.txt',
    description='Slice an image into rectangles sutable for tiled printing.',
    long_description=open('README.txt').read(),
    install_requires=[
        "PIL >= 1.1.6",
    ],
)