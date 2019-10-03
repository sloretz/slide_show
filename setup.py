from setuptools import setup

package_name = 'slide_show'

setup(
    name=package_name,
    version='0.1.0',
    packages=['slide_show'],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    author='Shane Loretz',
    author_email='sloretz@openrobotics.org',
    maintainer='Shane Loretz',
    maintainer_email='sloretz@openrobotics.org',
    keywords=['ROS'],
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
    ],
    description='Publishes images from the file system.',
    license='Apache License, Version 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'slide_show = slide_show:main',
        ],
    },
)
