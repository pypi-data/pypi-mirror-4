from distutils.core import setup

f=open("README")

setup(
    name='pynomenklatura',
    version='0.2',
    description="Client library for nomenklatura, make record linkages on the web.",
    long_description="\n".join(f),
    classifiers=[
        ],
    keywords='data mapping identity linkage record',
    author='Open Knowledge Foundation',
    author_email='info@okfn.org',
    url='http://okfn.org',
    license='AGPLv3',
    py_modules=['nomenklatura'],
    zip_safe=False,
    install_requires=[
        "requests>=0.12"
    ],
    tests_require=[],
    entry_points=\
    """ """,
)
