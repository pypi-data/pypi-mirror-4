from setuptools import setup


setup(
    name='fubar',
    version='0.1.0',
    description="PBKDF2-AES-CTR-HMAC-SHA256-RSA-PKCS#1-OAEP-PSS-bencode wrapper",
    py_modules=['fubar'],
    license="MIT",
    install_requires=[
        'pycrypto>=2.6',
        'bencode>=1.0',
    ],
)
