
import os

codedir = os.path.dirname(__file__)
(head,tail) = os.path.split(codedir)
if tail == 'library.zip': # Windows?
    codedir = head
elif tail == 'site-packages.zip': # Mac app
    codedir = head

