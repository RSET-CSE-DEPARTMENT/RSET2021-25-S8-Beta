import pyAesCrypt
import os
from django.core.files.storage import FileSystemStorage
import shutil

import time
enc_pass="please-use-a-long-and-random-password"

def encrypt(fle,fss,password):
    pyAesCrypt.encryptFile(fle,fss,password)

def decrypt(fles,fss,password):
    pyAesCrypt.decryptFile(fles,fss,password)

               