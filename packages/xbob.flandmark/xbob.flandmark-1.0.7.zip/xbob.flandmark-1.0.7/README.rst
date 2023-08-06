==============================
 Python Bindings to flandmark
==============================

This package is a simple Boost.Python wrapper to the (rather quick) open-source
facial landmark detector `flandmark
<http://cmp.felk.cvut.cz/~uricamic/flandmark/index.php>`_, **version 1.0.7**
(or the github state as of 10/february/2013).
If you use this package, the author asks you to cite the following paper::

  @inproceedings{Uricar-Franc-Hlavac-VISAPP-2012,
    author =      {U{\\v{r}}i{\\v{c}}{\\'{a}}{\\v{r}}, Michal and Franc, Vojt{\\v{e}}ch and Hlav{\\'{a}}{\\v{c}}, V{\\'{a}}clav},
    title =       {Detector of Facial Landmarks Learned by the Structured Output {SVM}},
    year =        {2012},
    pages =       {547-556},
    booktitle =   {VISAPP '12: Proceedings of the 7th International Conference on Computer Vision Theory and Applications},
    editor =      {Csurka, Gabriela and Braz, Jos{\'{e}}},
    publisher =   {SciTePress --- Science and Technology Publications},
    address =     {Portugal},
    volume =      {1},
    isbn =        {978-989-8565-03-7},
    book_pages =  {747},
    month =       {February},
    day =         {24-26},
    venue =       {Rome, Italy},
    keywords =    {Facial Landmark Detection, Structured Output Classification, Support Vector Machines, Deformable Part Models},
    prestige =    {important},
    authorship =  {50-40-10},
    status =      {published},
    project =     {FP7-ICT-247525 HUMAVIPS, PERG04-GA-2008-239455 SEMISOL, Czech Ministry of Education project 1M0567},
    www = {http://www.visapp.visigrapp.org},
  }

You should also cite `Bob <http://www.idiap.ch/software/bob/>`_, as a core
framework::

  @inproceedings{Anjos_ACMMM_2012,
    author = {A. Anjos AND L. El Shafey AND R. Wallace AND M. G\"unther AND C. McCool AND S. Marcel},
    title = {Bob: a free signal processing and machine learning toolbox for researchers},
    year = {2012},
    month = oct,
    booktitle = {20th ACM Conference on Multimedia Systems (ACMMM), Nara, Japan},
    publisher = {ACM Press},
    url = {http://publications.idiap.ch/downloads/papers/2012/Anjos_Bob_ACMMM12.pdf},
  }

Installation
------------

You can just add a dependence for ``xbob.flandmark`` on your ``setup.py`` to
automatically download and have this package available at your satellite
package. This works well if Bob_ is installed centrally at your machine. 

Otherwise, you will need to tell ``buildout`` how to build the package locally
and how to find Bob_. For that, just add a custom egg recipe to your
buildout that will fetch the package and compile it locally, setting the
buildout variable ``prefixes`` to where Bob_ is installed (a build directory
will work as well). For example::

  [buildout]
  parts = flandmark <other parts here...>
  ...
  prefixes = /Users/andre/work/bob/build/debug

  ...

  [flandmark]
  recipe = xbob.buildout:develop

  ...

Development
-----------

To develop these bindings, you will need the open-source library Bob_ installed
somewhere. At least version 1.1 of Bob is required. If you have compiled Bob
yourself and installed it on a non-standard location, you will need to note
down the path leading to the root of that installation.

Just type::

  $ python bootstrap.py
  $ ./bin/buildout

If Bob is installed in a non-standard location, edit the file ``buildout.cfg``
to set the root to Bob's local installation path. Remember to use the **same
python interpreter** that was used to compile Bob, then execute the same steps
as above.

Usage
-----

Pretty simple, just do something like::

  import bob
  from xbob import flandmark

  video = bob.io.VideoReader('myvideo.avi')
  localize = flandmark.Localizer()

  for frame in video:
    print localize(frame)
