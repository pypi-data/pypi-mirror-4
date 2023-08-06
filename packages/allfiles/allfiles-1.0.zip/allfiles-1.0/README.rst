############################################
allfiles: Iterate files in directory trees
############################################
allfiles privites functions which iterate files or directories
in direcotory trees.
The code of allfiles is almost a recipe 2.17 "Walking Directory Trees" in Python Cookbook, 2nd Edition.
However, it is modified as my wish.

Example
=======
::
  >>> from allfiles import allfiles
  >>> allfiles('C:\Python32\lib')
  <generator object allfiles at 0x02C8A2B0>
  >>> for f in allfiles('C:\Python32\lib'):
  ...     print(f)
  ...
  C:\Python32\lib\abc.py
  C:\Python32\lib\aifc.py
  C:\Python32\lib\antigravity.py
  C:\Python32\lib\argparse.py
  C:\Python32\lib\ast.py
  C:\Python32\lib\asynchat.py
  C:\Python32\lib\asyncore.py
  C:\Python32\lib\base64.py
  C:\Python32\lib\bdb.py
  C:\Python32\lib\binhex.py
     (and more files...)

