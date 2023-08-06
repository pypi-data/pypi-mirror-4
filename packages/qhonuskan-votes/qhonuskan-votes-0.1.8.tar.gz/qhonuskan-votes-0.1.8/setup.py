from setuptools import setup

setup(
    name="qhonuskan-votes",
    url='https://github.com/linkfloyd/qhonuskan-votes',
    license='GPL',
    description="Easy to use reddit like voting system for django models.",
    long_description=open('README.rst', 'r').read(),
    author='Mirat Can Bayrak',
    author_email='miratcanbayrak@gmail.com',
    packages=['qhonuskan_votes', 'qhonuskan_votes.templatetags'],
    package_data={'qhonuskan_votes': ['templates/*.html', 'static/*.css']},
    version='0.1.8',
    requires=['django(>=1.2)'],
    zip_safe=True,
    include_package_data=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Environment :: Web Environment',
        'Framework :: Django',
    ],
)
