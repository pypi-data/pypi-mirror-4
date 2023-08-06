from setuptools import setup, find_packages
readme = None
try:
    with open("README.md") as readme_md:
        readme = readme_md.read()
except:
    readme = """
    MultiString is a Python class which allows a single string to operate in many different contexts. A good use case for this would be for the interchange of the same string in many different languages.

    The MultiString object itself can use any valid string method, and the method will only affect the currently active context, meaning MultiStrings can be used as-is with any existing code. Additionally, MultiStrings are very protective of their contexts. An inactive context may not be manipulated in any way, preventing you from accidentally overwriting valuable information.

    MultiStrings also offer bindings to translate contexts on the fly.

    MultiStrings have full support for slicing and concatenation, and even use the native reversed function, to return the string backwards."""

setup(
        name = "MultiString",
        version = "0.1.3",
        description="MultiString is a class that allows strings to take on different meanings depending on their context.",
        long_description = readme,    
        author="Tom A. Thorogood",
        author_email="tom@tomthorogood.com",
        license="GPLv3",
        url = "http://www.github.com/tomthorogood/MultiString",
        test_suite = 'MSTestCase',
        packages = find_packages(exclude=['setup.py','tests']),
        zip_safe = True
)

