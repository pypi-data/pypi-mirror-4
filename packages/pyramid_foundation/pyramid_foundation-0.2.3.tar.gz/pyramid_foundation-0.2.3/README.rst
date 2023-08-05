`pyramid_foundation <http://github.com/ppinette/pyramid_foundation>`_
============================================================================

This package provides a Pyramid scaffold which includes `Zurb Foundation <http://foundation.zurb.com/>`_

pyramid_foundation is intended to extend other scaffolds such as starter or alchemy. Using it alone will not create a Pyramid project.


Getting Started
---------------

    $ pcreate -s <scaffold> -s pyramid_foundation <project_name>

Your newly created project will have the Foundation files located in Project/package/static/ 

Additionally, mytemplate.pt has been modified to include the Foundation CSS and JS along with the standard basic introduction to Foundation. 

Compass/Sass
------------

In order to use Compass, you'll need to install the Compass and Foundation gems

    $ gem install compass  
    $ gem install foundation

pyramid_foundation includes a config.rb to manage your styles as a compass project. For more information visit:

* `Compass-style.org <http://compass-style.org/>`_
* `Sass-lang.com <http://sass-lang.com/>`_  


Files
_____

* static/config.rb                     -       Compass config file
* static/css/package_name.css          -       Styles for included template
* static/css/app.css                   -       Complete Foundation styles compiled from Sass
* static/img/*                         -       Foundation images
* static/js/*                          -       Foundation Javascripts
* static/sass/package_name.scss        -       Sass styles for included template
* static/sass/_settings.scss           -       Foundation settings  
* static/sass/app.scss                  -       Foundation Sass styles  
* templates/mytemplate.pt              -       Example Pyramid template  
