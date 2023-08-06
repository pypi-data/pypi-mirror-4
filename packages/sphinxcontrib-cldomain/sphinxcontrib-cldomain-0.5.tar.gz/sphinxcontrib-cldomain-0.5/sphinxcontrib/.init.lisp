(let ((quicklisp-init (merge-pathnames ".quicklisp/setup.lisp" (user-homedir-pathname)))) (load quicklisp-init))
(asdf:initialize-source-registry)
