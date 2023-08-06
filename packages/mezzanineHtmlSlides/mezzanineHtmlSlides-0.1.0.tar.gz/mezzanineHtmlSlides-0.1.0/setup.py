from setuptools import setup


setup(
    name='mezzanineHtmlSlides',
    version='0.1.0',
    license='Simplified BSD',

    install_requires = [
        'Mezzanine',
    ],

    description='Plug a html slideshow into your mezzanine website on all pages.',
    long_description=open('README.md').read(),

    author='Tonino Jankov',
    author_email='tyaakow@gmail.com',

    url='http://github.com/tjankov/mezzanineHtmlSlides',
    download_url='http://github.com/tjankov/mezzanineHtmlSlides/downloads',

    packages=['mezzaninehtmlslides'],

    zip_safe=False,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
