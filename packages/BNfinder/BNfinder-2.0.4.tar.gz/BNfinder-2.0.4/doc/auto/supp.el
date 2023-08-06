(TeX-add-style-hook "supp"
 (lambda ()
    (LaTeX-add-bibliographies
     "regul")
    (LaTeX-add-environments
     "theorem"
     "proposition"
     "alg"
     "ass")
    (TeX-add-symbols
     "N"
     "D"
     "G"
     "V"
     "Vc"
     "g"
     "OO"
     "X"
     "Y"
     "x"
     "vp"
     "PP"
     "E"
     "Pa")
    (TeX-run-style-hooks
     "amssymb"
     "amsmath"
     "graphicx"
     "inputenc"
     "utf8"
     "fontenc"
     "T1"
     "latex2e"
     "art10"
     "article"
     "methods")))

