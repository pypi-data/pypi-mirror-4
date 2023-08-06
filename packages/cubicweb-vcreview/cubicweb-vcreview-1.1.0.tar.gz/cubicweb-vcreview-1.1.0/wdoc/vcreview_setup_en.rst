
The idea is that you have two mercurial repositories, one holding the source code (the
source repository), the other holding the patches queue (the patch repository). You'll
have to have both of them modelized as cubicweb entities using vcsfile's
`Repository` entity type.

.. Note:: In the remaining of this documentation, we will denote these
   vcsfile `Repository` objects as `CWRepository` to distinguish them
   from mercurial ones.


Provided that you already have your source repository there, click 'add
patch repository' in the actions box. Give it a title and url.

.. Important::
   You **must** select the option "import revision content" here
   otherwise you won't see any patch (which makes the whole thing
   useless).


A background process will then import the repository content and
create corresponding `Patch` entities.

.. Note:: In the remaining of this documentation, we will denote these
   vcsfile `Patch` objects as `CWPatch` to distinguish them from
   mercurial ones.
