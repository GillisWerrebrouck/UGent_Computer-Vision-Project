# LaTeX setup

1. Install LaTeX: [https://www.latex-project.org/get/](https://www.latex-project.org/get/)
2. Clone this git repository
3. Install the plugin  `LaTeX Workshop` in VS Code
4. Open `settings.json`: ⌘ + Shift + P and search for `Open Settings (JSON)` (Windows users: probably `F1`)
5. Add the JSON below at the end of the `settings.json`
```json
"latex-workshop.latex.recipes":[
    {
        "name": "lualatex ➞ bibtex ➞ lualatex x 2",
        "tools": [
            "lualatex",
            "bibtex",
            "lualatex",
            "lualatex"
        ]
    },
    {
        "name": "lualatex ➞ bibtex ➞ makeglossaries ➞ lualatex x 2",
        "tools": [
            "lualatex",
            "bibtex",
            "makeglossaries",
            "lualatex",
            "lualatex"
        ]
    },
    {
        "name": "lualatex (zonder bibliografie)",
        "tools": [
            "lualatex",
            "lualatex"
        ]
    }
],
"latex-workshop.latex.tools":[
    {
        "name": "bibtex",
        "command": "bibtex",
        "args": [
            "%DOCFILE%"
        ],
        "env": {}
    },
    {
        "name": "makeglossaries",
        "command": "makeglossaries",
        "args": [
          "%DOCFILE%"
        ]
    },
    {
        "name": "lualatex",
        "command": "lualatex",
        "args": [
            "-interaction=nonstopmode",
            "--shell-escape",
            "%DOC%"
        ],
        "env": {}
    }
],
"latex-workshop.latex.autoBuild.run": "onFileChange",
"latex-workshop.latex.recipe.default": "lastUsed",
"latex-workshop.view.pdf.viewer": "tab",
"latex-workshop.latex.autoClean.run": "onBuilt",
"latex-workshop.latex.clean.fileTypes": [
    "**/.aux",
    "**/*.aux",
    "**/*.bbl",
    "**/*.blg",
    "**/*.idx",
    "**/*.ind",
    "**/*.lof",
    "**/*.lot",
    "**/*.out",
    "**/*.toc",
    "**/*.acn",
    "**/*.acr",
    "**/*.alg",
    "**/*.glg",
    "**/*.glo",
    "**/*.gls",
    "**/*.fls",
    "**/*.fdb_latexmk",
    "**/*.snm",
    "**/*.synctex(busy)",
    "**/*.synctex.gz(busy)",
    "**/*.nav",
    "**/*.lol",
    "**/*.tdo",
    "**/*.lop",
    "**/*.dvi",
    "**/*.ist",
    "**/*.glsdefs",
    "**/*.bib.bak",
    "_minted-main/*",
    "_minted-main"
]
```
6. Reload VS Code: ⌘ + Shift + P and search for 'Reload window' (Windows users: probably `F1`)
7. If you open `main.tex`, there should be an icon `TeX` in the sidebar on the left side of the screen
8. Click on the `TeX` icon and execute the command: `Build LaTeX project` -> `Recipe: lualatex -> bibtex -> makeglossaries -> lualatex x 2`
9. Now there should an updated `main.pdf` and all build files should be gone (except `main.log` for debugging purposes)
10. Install JabRef which is pretty handy for references (optional)
   -  MacOS: `brew cask install jabref`
   -  Windows: [https://www.jabref.org/](https://www.jabref.org/)
