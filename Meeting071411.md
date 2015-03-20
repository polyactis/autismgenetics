#Meeting with Doxa, Alden, Yeongshnn, Uemit. Mainly about how to utilize stuff Uemit has written for the standalone gwas app.

## Points ##

  1. general architecture of web app, separate into modules
    1. gwt-platform http://code.google.com/p/gwt-platform/
    1. command-pattern API for GWT http://code.google.com/p/gwt-dispatch/
    1. GWT injection http://code.google.com/p/google-gin/
    1. python wrapper for jbrowse json data structures for genes/gwas.
  1. migrate the standalone gwas app into google code
    1. currently at https://bzr.gmi.oeaw.ac.at/loggerhead/nordborg-group/gwas/
  1. how the hdf5 is handled in the server end? cache? dot product
    1. http://code.google.com/p/h5py/ some of numpy interface around hdf5, good for genotype matrix
  1. style sheets of GMI plone , who did that?
    1. Some guy spent a month (half-time employee).
    1. the better idea may just to outsource the style sheet thing to a  design company


## Documentation ##

Most of the components are on the web.

  1. https://github.com/timeu/GWASGeneViewer
  1. https://github.com/timeu/processing-js-gwt
  1. https://github.com/timeu/GeneViewer

The documentation is a bit poor. A complete web app (which is responsible for http://gwas.gmi.oeaw.ac.at/, code to be in google code), shows how these different components will be utilized.


### Useful youtube videos ###

  1. Google I/O 2009 Best Practices For Architecting Your GWT App http://www.youtube.com/watch?v=PDuhR18-EdM
  1. 2011 Google I/O highly-productive GWT http://www.youtube.com/watch?v=PDuhR18-EdM
  1. 2011 Google I/O high-performance GWT, best practices for writing smaller, faster apps http://www.youtube.com/watch?v=0F5zc1UAt2Y&feature=relmfu
  1. model-view-presenter framework to simplify your next GWT project. http://code.google.com/p/gwt-platform/