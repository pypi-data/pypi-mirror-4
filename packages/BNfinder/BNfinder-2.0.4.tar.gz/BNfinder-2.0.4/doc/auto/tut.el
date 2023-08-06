(TeX-add-style-hook "tut"
 (lambda ()
    (LaTeX-add-bibliographies
     "regul")
    (TeX-run-style-hooks
     "graphicx"
     "inputenc"
     "utf8"
     "fontenc"
     "T1"
     "latex2e"
     "howto10"
     "howto"
     "tutor")))

