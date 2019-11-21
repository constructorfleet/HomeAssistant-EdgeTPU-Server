import setuptools

from edgetpu_server.const import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='edgetpu_server',
    version=__version__,
    license='MIT',
    url='https://github.com/constructorfleet/HomeAssistant-EdgeTPU-Server',
    author='Teagan Glenn',
    author_email='that@teagantotally.rocks',
    description='Performs object detection using an Edge Tensor Processing Unit on a video stream'
                ' and publishes the state to a specified Home-Assistant instance.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'certifi==2019.9.11',
        'chardet==3.0.4',
        'ConfigArgParse==0.15.1',
        'idna==2.8',
        'imutils==0.5.3',
        'numpy==1.17.4',
        'opencv-python==4.1.1.26',
        'Pillow==6.2.1',
        'requests==2.22.0',
        'urllib3==1.25.7'
    ],
    test_suite='tests',
    keywords=['home-assistant', 'coral', 'edgetpu'],
    entry_points={
        'console_scripts': [
            'edgetpu-server = edgetpu_server.__main__:main'
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Topic :: Home Automation',
    ],
)