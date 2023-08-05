from distutils.core import setup

setup(
    name="matchsticks",
    version="0.0.1",
    description="Complex argument matchers for use with mock",
    author="Alex Good",
    author_email="alexjsgood@gmail.com",
    url="https://github.com/alexjg/matchsticks",
    py_modules=["matchsticks"],
    requires=["mock"],
    license="MIT License",
)
