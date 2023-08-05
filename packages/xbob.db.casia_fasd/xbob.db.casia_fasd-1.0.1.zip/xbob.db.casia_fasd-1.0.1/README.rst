===================================
 CASIA Face Anti-Spoofing Database
===================================

The CASIA-FASD database is a spoofing attack database which consists of three
types of attacks: warped printed photographs, printed photographs with cut eyes
and video attacks. The samples are taken with three types of cameras: low
quality, normal quality and high quality.

The actual raw data for the database should be downloaded from the original
URL. This package only contains the `Bob <http://www.idiap.ch/software/bob/>`_
accessor methods to use the DB directly from python, with our certified
protocols.

References::

  1. Z. Zhang, J. Yan, S. Lei, D. Yi, S. Z. Li: "A Face Antispoofing Database
     with Diverse Attacks", In proceedings of the 5th IAPR International
     Conference on Biometrics (ICB'12), New Delhi, India, 2012.

You would normally not install this package unless you are maintaining it. What
you would do instead is to tie it in at the package you need to **use** it.
There are a few ways to achieve this:

1. You can add this package as a requirement at the ``setup.py`` for your own
   `satellite package
   <https://github.com/idiap/bob/wiki/Virtual-Work-Environments-with-Buildout>`_
   or to your Buildout ``.cfg`` file, if you prefer it that way. With this
   method, this package gets automatically downloaded and installed on your
   working environment, or

2. You can manually download and install this package using commands like
   ``easy_install`` or ``pip``.

The package is available in two different distribution formats:

1. You can download it from `PyPI <http://pypi.python.org/pypi>`_, or

2. You can download it in its source form from `its git repository
   <https://github.com/bioidiap/xbob.db.casia_fasd>`_. When you download the
   version at the git repository, you will need to run a command to recreate
   the backend SQLite file required for its operation. This means that the
   database raw files must be installed somewhere in this case. With option
   ``a`` you can run in `dummy` mode and only download the raw data files for
   the database once you are happy with your setup.

You can mix and match points 1/2 and a/b above based on your requirements. Here
are some examples:

Modify your setup.py and download from PyPI
===========================================

That is the easiest. Edit your ``setup.py`` in your satellite package and add
the following entry in the ``install_requires`` section (note: ``...`` means
`whatever extra stuff you may have in-between`, don't put that on your
script)::

    install_requires=[
      ...
      "xbob.db.casia_fasd",
    ],

Proceed normally with your ``boostrap/buildout`` steps and you should be all
set. That means you can now import the namespace ``xbob.db.casia_fasd`` into your
scripts.

Modify your buildout.cfg and download from git
==============================================

You will need to add a dependence to `mr.developer
<http://pypi.python.org/pypi/mr.developer/>`_ to be able to install from our
git repositories. Your ``buildout.cfg`` file should contain the following
lines::

  [buildout]
  ...
  extensions = mr.developer
  auto-checkout = *
  eggs = bob
         ...
         xbob.db.casia_fasd

  [sources]
  xbob.db.casia_fasd = git https://github.com/bioidiap/xbob.db.casia_fasd.git
  ...
