from setuptools import setup
readme = open('README.rst').read()

setup(name='googlegantt',
        version='0.6.1',
        author='Adam Bard',
        author_email='adam@adambard.com',
        license='MIT',
        description='Produce Gantt charts using the Google Charts API',
        long_description=readme,
        py_modules=['googlegantt'],
        install_requires=[
            "PIL",
        ],
)

