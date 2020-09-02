# SKBS templates for hrprotoparser

This repository provides skbs templates for hrprotoparser.

To install them, just do :

    for i in hrpp*; do skbs install --symlink $i; done

# USAGE

to use one of these template, do the following :

    skbs gen @hrpp_C <dest> -- -p protocol.hrp

where `@hrpp_C` can be replaced by any hrpp template, and `<dest>` is the destination directory.

to get help, simply do :

    skbs gen @hrpp_C <dest> -- --help
  
You can also simply print the protocol content with :

    skbs gen @hrpp_C <dest> -- --info

# License

Copyright 2014-2020 © Léo Flaventin Hauchecorne

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


