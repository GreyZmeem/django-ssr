import setuptools


setuptools.setup(
    name='django_ssr',
    version='0.0.1',
    author='Andrey Maslov',
    author_email='greyzmeem@gmail.com',
    license='MIT',
    description='SSR for django project',
    url='https://github.com/greyzmeem/django-ssr',
    packages=['django_ssr'],
    python_requires='>=3.5,<3.8',
    install_requires=[
        'django>=1.11,<2.2',
        'requests>=2',
    ],
    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'License :: OSI Approved :: MIT License',
    ),
)
