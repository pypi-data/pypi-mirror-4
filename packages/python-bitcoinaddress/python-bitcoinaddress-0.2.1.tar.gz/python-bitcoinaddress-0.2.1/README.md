python-bitcoinadress
====================
Bitcoin address validation

2012-12-14 R.R. Nederhoed
https://github.com/nederhoed/python-bitcoinadress
Please give feedback.


Original author probably:
 http://paddy3118.blogspot.nl/2012/11/some-identities-for-python-inttobytes.html

Copied from: 
 http://rosettacode.org/wiki/Bitcoin/address_validation#Python

I packaged it to be available to everyone via The Cheese Shop (pypi):
 http://pypi.python.org/pypi/python-bitcoinaddress


History
-------
### 2012-12-14
* I renamed the `check_bc` function to `validate` for ease of use.
* Added check if the base58-re-encoded address matches the original address
  Relevant for short addresses with a valid check, but invalid format.
  For example: 
    14oLvT2
  The valid version of that address is:
    1111111111111111111114oLvT2
* Added alternatives for `long.to_bytes` and `long.from_bytes` for Python 
  versions prior to 3.2
* Added unit tests

