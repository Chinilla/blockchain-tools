from setuptools import setup

if __name__ == '__main__':
    setup(
        name='blockchain_tools',
        version='0.0.1',
        packages=[
            'blockchain_tools'
        ],
        url='https://github.com/zqrx/blockchain-tools',
        license='GNU General Public License v2.0',
        author='zqrx',
        author_email='',
        description='',
        install_requires=[
            'click~=7.1.2',
            'chia-blockchain~=1.2.3',
            'setuptools~=57.0.0',
            'requests~=2.26.0'
        ],
        entry_points={
            'console_scripts': [
                'blockchain-tools = blockchain_tools.blockchain_tools:main',
                'flora-dev-cli = blockchain_tools.blockchain_tools:main'
            ]
        }
    )
