from distutils.core import setup

setup(
    name='YetAnotherImageResizer',
    version='0.0.0',
    author='Mathieu Roche',
    author_email='mathieu.roche-site@laposte.net',
    packages=['imageresizer', 'imageresizer.test'],
    package_data = {'imageresizer':['logger.ini']},
    scripts = [ "bin/imageresizer" ],
    url='http://pypi.python.org/pypi/YetAnotherPiwigoImageResizer/',
    license='LICENSE.txt',
    description='Image resizer for Piwigo with Tk UI.',
    long_description=open('README.txt').read(),
    install_requires=[
        "PIL >= 1.1.6",
    ],
)
