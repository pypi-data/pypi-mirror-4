.. -*-rst-*-

Zencheck
========

A simple application for syntax-checking python files.  pyflakes_ is
used for error-checking and pep8_ is used for style checking (produces
warnings).

.. _pep8: http://pypi.python.org/pypi/pep8
.. _pyflakes: http://pypi.python.org/pypi/pyflakes

Improvments Over Stock PyFlakes/pep8 With Flymake Mode
------------------------------------------------------

  * pyflakes warnings are now shown as flymake warnings (not the case with
    standard flymake/pyflakes integration)
  * integrates both pyflakes and pep8 in one command

Latest Working Versions
-----------------------

  * Python 2.7.3
  * pyflakes 0.5.0
  * pep8 1.3.3

*Note: As long as the api's of neither pyflakes or pep8 changes, future
versions should work.*

Example .emacs Setup
--------------------

::

    (require 'flymake)

    (custom-set-variables
     '(flymake-allowed-file-name-masks
       (quote (("\\.c\\'" flymake-simple-make-init)
               ("\\.cpp\\'" flymake-simple-make-init)
               ("\\.xml\\'" flymake-xml-init)
               ("\\.html?\\'" flymake-xml-init)
               ("\\.cs\\'" flymake-simple-make-init)
               ("\\.p[ml]\\'" flymake-perl-init)
               ("\\.php[345]?\\'" flymake-php-init)
               ("\\.h\\'" flymake-master-make-header-init flymake-master-cleanup)
               ("\\.java\\'" flymake-simple-make-java-init flymake-simple-java-cleanup)
               ("[0-9]+\\.tex\\'" flymake-master-tex-init flymake-master-cleanup)
               ("\\.tex\\'" flymake-simple-tex-init)
               ("\\.idl\\'" flymake-simple-make-init)
               ("\\.py\\'" flymake-zencheck-init)))))

    (defun flymake-zencheck-init ()
      (let* ((temp-file (flymake-init-create-temp-buffer-copy
                         'flymake-create-temp-inplace))
             (local-file (file-relative-name
                          temp-file
                          (file-name-directory buffer-file-name))))
        (list "zencheck" (list local-file))))

    (add-hook 'find-file-hook 'flymake-find-file-hook)

    (defun flymake-init-vars-hook ()
      (setq flymake-err-line-patterns
            (cons
             (quote ("^\\(.*?\\):\\([0-9]+\\):\\([0-9]+\\):\\(.*\\)" 1 2 3 4))
             flymake-err-line-patterns)))

    (add-hook 'find-file-hook 'flymake-init-vars-hook)


Credits
-------

  * Rocky Burt (rocky AT serverzen DOT com) - maintainer
