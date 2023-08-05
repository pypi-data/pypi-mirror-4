Introduction
============
This product allows you to make sites faster since you don't need to worry about some of the hang ups from Internet Explorer. 

This Product works in Plone 2.5, 3, 4+

1.) If you want to use transparent pngs for your IE6 sites add the following to a dtml method css stylesheet
::
   
   /* <dtml-with base_properties> (do not remove this :) */
   /* <dtml-call "REQUEST.set('portal_url', portal_url())"> (not this either :) */
    *html  img, div, a, input { behavior: url(&dtml-portal_url;/iepngfix.htc); } to a IE6 only stylesheet.
    /* </dtml-with> */ 

2.) New features include being able to do CSS 3 (Uses css3pie http://css3pie.com/) type things in IE 6,7,8. Things like border-radius, box-shadow, text-shadow.

A.) To use the CSS 3 features make a ie only css file and add your file into the css area of main_template. In Plone 4 you can just add the condition for the css registry file.
        <!--[if lt IE 9]><link href="IEFixes_foo.css"  media="screen" type="text/css" rel="stylesheet"> <![endif]-->
        
B.) Add these 2 lines to your css class or id.
::

    behavior: url(&dtml-portal_url;/PIE.htc);
    position: relative;

Make a list of classes that need to be changed in IE in your IEFixes_foo.css file. Example
::

    #portal-personaltools,
    .portalHeader,
    .fooclass {
     behavior: url(&dtml-portal_url;/PIE.htc); 
        position: relative; 
        }

C.)  Issues with CSSPie.. You can't do less then all four border-radius easily::

    .portalHeader {
    border-top-left-radius: 10px;
    border-bottom-left-radius: 10px;
    }

should be::

    .portalHeader {
        border-radius: 10px 0px 0px 10px;
    }
    

Also, if you are are doing gradients there is a hook::

    #portal-header {
        -pie-background: linear-gradient(#D3D4D5, #FEFEFE); /*PIE*/ 
    }
    

