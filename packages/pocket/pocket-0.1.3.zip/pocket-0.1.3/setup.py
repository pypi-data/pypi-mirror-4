from setuptools import setup

setup(
    name = "pocket", # easy_install pocket
    description = "api wrapper for getpocket.com",
    #long_description=open('README.md', 'rt').read(),
    long_description = '''
    <h1>Pocket</h1>

    <p>A python wrapper for the <a href="http://getpocket.com/api/docs">pocket api</a>.</p>

    <h2>Installation</h2>

    <p><code>
    pip install pocket
    </code></p>

    <h2>Usage</h2>

    <p>First, you'll need your pocket api key. You can find this from your account page.
    Then, you need to create an instance of the pocket object</p>

    <p>```python
    import pocket</p>

    <p>pocket<em>instance = pocket.Pocket(username, password, api</em>key)
    ```</p>

    <p>For detailed documentation of the methods available, please visit the official <a href="http://getpocket.com/api/docs">pocket api documentation</a>.</p>
    ''',

    # version
    # third part for minor release
    # second when api changes
    # first when it becomes stable someday
    version = "0.1.3",
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
