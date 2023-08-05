from distutils.core import setup

setup(
    name='tweepy-utils',
    version='0.1dev4',
    description='A set of Python utility scripts for Twitter account management, using Tweepy.',
    author='Audrey Roy',
    author_email='audreyr@cartwheelweb.com',
    url='https://github.com/audreyr/tweepy-utils/',
    # packages=['tweepy_utils',],
    license='MIT license',
    scripts=['scripts/list-nonfollowers', 'scripts/unfollow-nonfollowers'],
    # long_description=open('README.md').read(),
)
