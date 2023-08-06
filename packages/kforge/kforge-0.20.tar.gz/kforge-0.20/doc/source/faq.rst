====
FAQ
====

1. kforge installs fine but I have problems getting Apache working and have
error messages like:

        ExtractionError: Can't extract file(s) to egg cache

        The following error occurred while trying to extract file(s) to the
        Python egg cache:

        [Errno 13] Permission denied: '/var/www/.python-eggs'

        The Python egg cache directory is currently set to:

          /var/www/.python-eggs

        Perhaps your account does not have write access to this directory?
        You can change the cache directory by setting the PYTHON_EGG_CACHE
        environment variable to point to an accessible directory.

   This problem arises if kforge was installed as a zipped python egg but
   apache/modpython does not have the right permissions to create an egg cache
   where it can unzip the egg.

   The easiest way to fix this is to break open the kforge egg file by
   unzipping it. Alternatively you can just reinstall kforge unzipped: 
  
       $ sudo easy_install -UZ kforge

   The use of the -Z option ensures that the kforge egg is installed unzipped.

2. Is there a debian package available?

   Yes there is courtesy of Martin Fuzzy. See this post for details:
   <http://www.kforgeproject.com/archive/2008/03/17/kforge-debian-package/>

