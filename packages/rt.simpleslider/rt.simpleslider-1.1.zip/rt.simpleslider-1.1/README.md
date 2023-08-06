rt.simpleslider Package Readme
==============================

Overview
--------

This products adds a simple slider support based on jQuery plugin called 
[Basic jQuery Slider](http://basic-slider.com/)


Using rt.simpleslider
---------------------

Simpleslider adds support for basic Plone types such as:
 * `Image`
 * `Topic`
 * `Folder`
 * `collective.contentleadimage`
 * `redturtle.smartlink`

Depends which type of object you will choose slider will generate proper HTML
snippet for you. In case of `ATImage` or objects that provides `ILeadImageable` 
you will get a single image. In case of `Topic` or `Folder` the slider with try to render
all items provided by query/folderlisting.


Viewlet
-------

Slider registers one viewlet to render the basic slider, default for `IAboveContent`:

```xml
    <browser:viewlet
        for="*"
        name="rt.simpleslider.slider"
        manager="plone.app.layout.viewlets.interfaces.IAboveContent"
        class=".viewlets.Slider"
        template="slider_viewlet.pt"
        layer="..interfaces.IBrowserLayer"
        permission="zope2.View"
    />
```
