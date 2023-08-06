from setuptools import setup, find_packages

setup(
    name='collagram',
    version='0.1.1',
    url='http://github.com/vurbmedia/collagram/',
    license='ISC',
    author='Adam Patterson',
    author_email='adam@adamrt.com',
    description='Generate collages of Instagram photographs.',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'PIL',
        'python-instagram'
    ],
)
