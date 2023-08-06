# use setuptools from distribute
from setuptools import setup
setup(
    name='pyotsu',
    version='0.0.3',
    description='Python Open Text Search Utility',
    author='Kenboo',
    author_email='kenbooing@gmail.com',
    url='http://com.nicovideo.jp/community/co1995667',
    packages=['pyotsu'],
    package_dir={'pyotsu': 'src/pyotsu'},
    package_data={'pyotsu': ['data/*.dat']},
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development ',
        ],
)
