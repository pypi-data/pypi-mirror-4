(TeX-add-style-hook "man"
 (lambda ()
    (LaTeX-add-bibliographies
     "regul")
    (LaTeX-add-environments
     "theorem"
     "proposition"
     "alg"
     "ass")
    (LaTeX-add-labels
     "sec:man")
    (TeX-add-symbols
     "N"
     "D"
     "G"
     "V"
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
     "howto10"
     "howto"
     "manual")))

