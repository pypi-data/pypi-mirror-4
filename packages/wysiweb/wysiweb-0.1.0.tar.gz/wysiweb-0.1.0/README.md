Use a directory full of template files to create a webpage:

www/index.mako is accessible by /
www/blog.mako is accessible by /blog/
www/blog/2013-03-08 is accessible by /blog/2013-03-08/

using the freeze function, you turn this into a directory of static files servable by something like apache or nginx
without going through  python route processing. See the example in example/ or http://github.com/openscienceframework/centerforopenscience.org
