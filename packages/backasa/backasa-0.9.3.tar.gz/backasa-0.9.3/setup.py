from distutils.core import setup

setup(
    name='backasa',
    version='0.9.3',
    author='Jonathan Johnson',
    author_email='me@jondavidjohn.com',
    packages=['backasa'],
    scripts=['bin/backasa'],
    url='https://github.com/jondavidjohn/backasa',
    download_url = 'https://github.com/jondavidjohn/backasa/tarball/master',
    keywords = ['picasa', 'backup', 'web album'],
    classifiers = [
        'Environment :: Console',
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: System :: Archiving :: Backup',
        'Topic :: System :: Archiving :: Mirroring',
    ],
    license='LICENSE.txt',
    description='A Picasa Web Albums backup utility',
    long_description=open('README.txt').read(),
    install_requires=[
        "gdata >= 2.0.17",
    ],
)
