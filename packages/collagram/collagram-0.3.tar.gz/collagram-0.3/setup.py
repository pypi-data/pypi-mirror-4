from distutils.core import setup

setup(
    name='collagram',
    version='0.3',
    author='Adam Patterson',
    author_email='adam@adamrt.com',
    url='http://github.com/vurbmedia/collagram/',
    license='ISC',
    description='Generate collages of Instagram photographs.',
    packages=['collagram', 'collagram.test'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'PIL',
        'python-instagram'
    ],
)
