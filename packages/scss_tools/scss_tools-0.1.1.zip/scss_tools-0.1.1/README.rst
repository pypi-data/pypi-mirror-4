SCSS Tools
==========

SCSS Tools is a bundle of tools for making web development with SCSS in Python much easier. It monitors your SCSS file directory for file change and recompile automatically for you. It also has Compass and Blueprint CSS framework built-in, To use SCSS Tools, you need to write a YAML configuration file. Following is an example of configuration file

example/scss.yaml::

    ---
    
    monitor:
        # path to Scss directory for monitoring
        scss_dir:
            scss
        
    compiler:
        # verbosity of message output
        verbosity: 2
        
        # compress
        compress: True
        
        # debug info
        debug_info: False
    
        # root of static files
        static_root:
            static
            
        # directory to output sprite images
        asset_root:
            static/asset
            
        # paths to import
        load_paths: [
            static/scss
        ]
            
        # path of input files and path of file to output 
        scss_files: [
            [scss/style.scss, static/style.css],
            [scss/style2.scss, static/style2.css],
        ]
    
    ...

To start monitoring and compiling SCSS, just type::

    scss_monitor -c scss.yaml

The path to configuration is scss.yaml, so you can also type::

    scss_monitor
    
It has built-in Compass/Blueprint SCSS framework, therefore, you can leverage
them directly

example/scss/style.scss::

    @import "compass/reset";
   
    @include blueprint-global-reset;
    
And you will get 

example/static/style.css::

    a, abbr, acronym, address, applet, article, aside, audio, b, big,
    blockquote, body, canvas, caption, center, cite, code, dd, del,
    details, dfn, div, dl, dt, em, embed, fieldset, figcaption, figure,
    footer, form, h1, h2, h3, h4, h5, h6, header, hgroup, html, i, iframe,
    img, ins, kbd, label, legend, li, mark, menu, nav, object, ol, output,
    p, pre, q, ruby, s, samp, section, small, span, strike, strong, sub,
    summary, sup, table, tbody, td, tfoot, th, thead, time, tr, tt, u, ul,
    var, video {
      margin: 0;
      padding: 0;
      border: 0;
      font-size: 100%;
      font: inherit;
      vertical-align: baseline;
    }
    body {
      line-height: 1;
    }
    ol, ul {
      list-style: none;
    }
    table {
      border-collapse: collapse;
      border-spacing: 0;
    }
    caption, td, th {
      text-align: left;
      font-weight: normal;
      vertical-align: middle;
    }
    blockquote, q {
      quotes: none;
    }
    blockquote:after, blockquote:before, q:after, q:before {
      content: "";
      content: none;
    }
    a img {
      border: none;
    }
    article, aside, details, figcaption, figure, footer, header, hgroup,
    menu, nav, section, summary {
      display: block;
    }

Installation
============

To install SCSS Tools, you can type::

    pip install scss_tools

If you perfer easy_install, then type::

    easy_install scss_tools

Commands
========

scss_compile
------------

Compile SCSS into CSS files.

scss_monitor
------------

Monitor and compile SCSS into CSS files.  

Source code
-----------

Source code is available at `Bitbucket <https://bitbucket.org/victorlin/scss_tools>`_.