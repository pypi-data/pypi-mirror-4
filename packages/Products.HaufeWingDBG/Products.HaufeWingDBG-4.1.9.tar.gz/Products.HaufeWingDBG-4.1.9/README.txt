Description
===========

This is a clone of the WingDBG product provided by Wingware as part of the (commercial) WingIDE product.
Copyright notice see Products\WingDBG\WingDBG.py, for Infos on WingIDE and WingDBG see 
http://www.wingware.com/doc/howtos/zope.

Reason for cloning WingDBG is a problem with monkeypatching TrustedFSPythonScript because of its use of
rebindFunction for method _write. The monkey patches applied by WingDBG/ScriptDebugging unfortunately do not work,
because Zope product TrustedExecutable is imported BEFORE WingDBG.


note: 
as of 2009-10-19, renaming WingDBG to HaufeWingDBG did not help, as probably tested with a Zope instance with already
patched CMFCore distribution; so the patch documented in TODO.txt is still necessary, until a workaround that remove this is found.

for WingIDE 3.2.1, Products.HaufeWingDBG-3.2.1_4dev_r155350-py2.4.egg is required

created 2009-10-13 /FRP
updated 2009-12-16 /FRP

