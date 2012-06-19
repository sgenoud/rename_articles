# Rename article

This is a small script for renamin scientific articles. It takes an article
path as argument and renames it if it can find a DOI code or arXiv ID in the
PDF. It renames it with the title of the article.  When no name is found, the
file name is not changed.

This script is provided as is and can eventually have bad results.

## Install

In order to run it need to have xpdf installed (the script depends on
pdftotext). A good way to install this command line tool on OS X is to have
[homebrew](http://mxcl.github.com/homebrew/) installed, and then execute:

```bash
brew install xpdf
```

If you want to automatically rename pdf articles added to a specific folder on
OS X, you can add a new folder action. For this open Automator.app and open the
"Rename Article" workflow provided in the utils folder. You can then change the
folder you want to apply the workflow to, as well as the path to the
rename_article script.

## License

MIT/X11
