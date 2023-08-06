
Naming patches
~~~~~~~~~~~~~~

**Name your patches with the '.diff' extension**, otherwise you won't
see the diff in vcreview until the file's content type has been
correctly set through the "modify" action. Also, notice the following
points:

* for commit message magic words explained below to work, patch name should
  match the regular expression '[-\.\w]+'

* patch renaming should be correctly handled,

* patches should be kept isolated in the branch they have been created
  in, otherwise you may have multiple CWPatch (patch entities) created
  for something that is actually a single patch.

Patches workflow
~~~~~~~~~~~~~~~~

When a patch is being constructed, the related CWPatches may be in
one of `in-progress` or `pending-review` states.

Finished CWPatches are in one of `applied`, `rejected` or `folded` states.

When a patch is deleted from the mercurial repository, the CWPatch is changed
to the `deleted` state. You should usually triage those CWPatches to one of
the above final states.

Automatic patch workflow handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Even if CWPatch objects can be manipulated directly
through the VCReview web interface, it is advised to use commit
messages that respects the rules described below and let VCReview
interpret them.

Note that a single commit message may concern several patches.

Submit a patch for review
+++++++++++++++++++++++++
You can either do it regularly through the web ui, or by having: ::

  "<patch path> ready for review"

on a line of the patch repository commit message. This will change the
CWPatch' state to `pending-review`.


Accepting a patch
+++++++++++++++++
You can either do it regularly through the web ui, or by having: ::

  "applied <patch path>"

on a line of the patch repository commit message. This will change the
CWPatch' state to `applied`.


Refusing a patch
++++++++++++++++
You can either do it regularly through the web ui, or by having: ::

  "refuse <patch path>"

on a line of the patch repository commit message. This will change the
CWPatch' state back to `in-progress`.


Rejecting a patch
+++++++++++++++++
You can either do it regularly through the web ui, or by having: ::

  "reject <patch path>"

on a line of the source repository commit message. This will change the
CWPatch' state to `rejected`.


Folding a patch
+++++++++++++++
When a patch is folded into another one, it should be marked as `folded`.
You can either do it regularly through the web ui, or by having: ::

  "fold <patch path>"

on a line of the source repository commit message. This will change the
CWPatch' state to `folded`.

Rebasing a patch
++++++++++++++++
When a patch is rebased or corrected to suit modifications from a parent patch,
if should be marked as `rebased`.
You can either do it regularly through the web ui, or by having: ::

  "rebase <patch path>"

on a line of the source repository commit message. This will let CWPatch
to its previous state.


Notification
~~~~~~~~~~~~
To be notified about CWPatches activity, you should mark yourself as `interested
in` each desired patch CWRepository.

