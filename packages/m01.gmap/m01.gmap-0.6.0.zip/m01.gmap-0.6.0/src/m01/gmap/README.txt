======
README
======

This package provides a z3c.form widget concept for google maps. For more info
about google maps see: http://code.google.com/apis/maps/.

The google map (GMapWidget) widget allows you to show a map for select latitude
and longitude for a geo location in input mode. In display mode it offers a
GMap which shows the given location.

As for all widgets, the GMap widget must provide the ``IWidget``
interface:

  >>> from zope.interface.verify import verifyClass
  >>> from z3c.form.interfaces import IWidget
  >>> from z3c.form.interfaces import INPUT_MODE
  >>> from m01.gmap.widget import GMapWidget

  >>> verifyClass(IWidget, GMapWidget)
  True

The widget can be instantiated only using the request:

  >>> from z3c.form.testing import TestRequest
  >>> request = TestRequest()

  >>> widget = GMapWidget(request)

Before rendering the widget, one has to set the name and id of the widget:

  >>> widget.id = 'widget.id'
  >>> widget.name = 'widget.name'

We also need to register the template for the widget:

  >>> import zope.component
  >>> from zope.pagetemplate.interfaces import IPageTemplate
  >>> from z3c.form.widget import WidgetTemplateFactory

  >>> import os
  >>> import m01.gmap
  >>> def getPath(filename):
  ...     return os.path.join(os.path.dirname(m01.gmap.__file__),
  ...     filename)

  >>> from m01.gmap import interfaces
  >>> zope.component.provideAdapter(
  ...     WidgetTemplateFactory(getPath('widget_input.pt'), 'text/html'),
  ...     (None, None, None, None, interfaces.IGMapWidget),
  ...     IPageTemplate, name=INPUT_MODE)

If we render the widget we get a simple input element:

  >>> print widget.render()
  <input type="hidden" id="widget.id-latitude" name="widget.name-latitude" class="hidden-widget" value="" />
  <input type="hidden" id="widget.id-longitude" name="widget.name-longitude" class="hidden-widget" value="" />
  <div id="widget.id" style="width: 400px; height: 300px"></div>
  <BLANKLINE>
  <script type="text/javascript">
    $("#widget\\.id").m01GMapWidget({
      iconWidth: 19,
      infoWindowAnchorYOffset: 0,
      iconHeight: 32,
      iconURL: "http://127.0.0.1/@@/m01GMapWidgetIcon.png",
      iconAnchorXOffset: 9,
      zoomFallback: 4,
      zoom: 11,
      longitude: null,
      longitudeFallback: 10,
      latitudeFallback: 10,
      latitudeExpression: "#widget\\.id-latitude",
      mode: "input",
      infoWindowContent: "Drag and drop the marker and save the form. <br />Double click the marker for remove them.",
      address: "",
      latitude: null,
      iconAnchorYOffset: 30,
      longitudeExpression: "#widget\\.id-longitude",
      iconShadowURL: "http://127.0.0.1/@@/m01GMapWidgetIconShadow.png",
      infoWindowAnchorXOffset: 10
    });
  </script>
  <BLANKLINE>
  <BLANKLINE>

We also need to include the IGMapAPIProvider wcih knows how to generate the
gamp api javascipt. The APi key it'self can get defined with a product config
or with a envirnoment setup. See buildout.cfg and util.py for more info:

  >>> import m01.gmap.util
  >>> m01.gmap.util.GMAP_API_KEY
  u'ABQIAAAAFAsu6H_TCNEapjedv-QILxTwM0brOpm-All5BF6PoaKBxRWWERQwU76rKRQO6OVZmsjxrqya2hcEBw'

We offer http or https javascript links:

  >>> print m01.gmap.util.GMAP_JAVASCRIPT
  <script type="text/javascript" src="//maps.google.com/maps?file=api&amp;v=2&amp;key=ABQIAAAAFAsu6H_TCNEapjedv-QILxTwM0brOpm-All5BF6PoaKBxRWWERQwU76rKRQO6OVZmsjxrqya2hcEBw"> </script>

  >>> print m01.gmap.util.GMAP_HTTPS_JAVASCRIPT
  <script type="text/javascript" src="https://maps.google.com/maps?file=api&amp;v=2&amp;key=ABQIAAAAFAsu6H_TCNEapjedv-QILxTwM0brOpm-All5BF6PoaKBxRWWERQwU76rKRQO6OVZmsjxrqya2hcEBw"> </script>

And you content provider can get used for render the full javascript:

  >>> import m01.gmap.browser
  >>> provider = m01.gmap.browser.GMapAPIProvider(None, None, None)
  >>> print provider.render()
  <script type="text/javascript" src="https://maps.google.com/maps?file=api&amp;v=2&amp;key=ABQIAAAAFAsu6H_TCNEapjedv-QILxTwM0brOpm-All5BF6PoaKBxRWWERQwU76rKRQO6OVZmsjxrqya2hcEBw"> </script>
