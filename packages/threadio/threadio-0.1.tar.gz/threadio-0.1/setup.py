from distutils.core import setup

try:
    import sys
    doc = ""
    if "sdist" in sys.argv:
        import threadio
        doc = threadio.__doc__
        while "[HIDE]" in doc:
            a, _, c = doc.partition("[HIDE]")
            doc = a + c.partition("[/HIDE]")[2]
except ImportError:
    pass

setup(
    name="threadio",
    version="0.1",
    author="EcmaXp",
    author_email="module-threadio@ecmaxp.pe.kr",
    description=(doc.strip().splitlines() or [""]).pop(0).strip(),
    long_description=doc.strip(),
    py_modules=["threadio"],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
