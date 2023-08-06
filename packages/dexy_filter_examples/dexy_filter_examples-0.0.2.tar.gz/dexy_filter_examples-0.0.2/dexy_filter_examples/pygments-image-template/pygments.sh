### @export "list-styles"
pygmentize -L styles

### @export "generate-css"
pygmentize -S manni -f html > manni.css
head -n 5 manni.css

### @export "generate-sty"
pygmentize -S manni -f latex > manni.sty
head -n 5 manni.sty
