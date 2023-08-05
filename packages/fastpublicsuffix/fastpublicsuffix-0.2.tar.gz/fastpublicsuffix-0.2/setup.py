from distutils.core import setup


setup(
    name='fastpublicsuffix',
    version='0.2',
    description='Fast Python interface to the Public Suffix List',
    author='Richard Boulton',
    author_email='richard@tartarus.org',
    url='https://github.com/rboulton/fastpublicsuffix',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    packages=['fastpublicsuffix'],
    package_dir={'fastpublicsuffix': 'fastpublicsuffix'},
    package_data={'fastpublicsuffix': ['public_suffix_list.txt']},
)
