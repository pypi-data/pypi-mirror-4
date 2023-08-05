from setuptools import setup

setup(
    name = "pocket", # easy_install pocket
    description = "api wrapper for getpocket.com",
    #long_description=open('README.md', 'rt').read(),
    long_description = '''
    Pocket
    ======

    A python wrapper for the [pocket api](http://getpocket.com/api/docs).

    Installation
    ------------
    ```
    pip install pocket
    ```

    Usage
    ------

    First, you'll need your pocket api key. You can find this from your account page.
    Then, you need to create an instance of the pocket object

    ```python
    import pocket

    pocket_instance = pocket.Pocket(username, password, api_key)
    ```

    For detailed documentation of the methods available, please visit the official [pocket api documentation](http://getpocket.com/api/docs).
    ''',

    # version
    # third part for minor release
    # second when api changes
    # first when it becomes stable someday
    version = "0.1.2",
    author = 'Tapan Pandita',
    author_email = "tapan.pandita@gmail.com",

    url = 'http://github.com/tapanpandita/pocket/',
    license = 'BSD',

    # as a practice no need to hard code version unless you know program wont
    # work unless the specific versions are used
    install_requires = ["argparse", "distribute", "requests", "wsgiref"],

    py_modules = ["pocket"],

    zip_safe = True,
)

# TODO: Do all this and delete these lines
# register: Create an accnt on pypi, store your credentials in ~/.pypirc:
#
# [pypirc]
# servers =
#     pypi
#
# [server-login]
# username:<username>
# password:<pass>
#
# $ python setup.py register # one time only, will create pypi page for pocket
# $ python setup.py sdist --formats=gztar,zip upload # create a new release
#
