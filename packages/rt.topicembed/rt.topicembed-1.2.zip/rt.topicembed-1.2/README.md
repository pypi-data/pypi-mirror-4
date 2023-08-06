rt.topicembed introduction
==========================

This product add's new tab to the topic content type called `embed`, and
publish topic's items similar to **twitter** widget.


Embed
-----

This is practically a simple form that allows user to configure a web widget.
The code can be found in the `textarea` in the same view. An example code
looks like that:

```html
<script>
    (function() {
        var s = document.createElement('script');
        s.src = 'http://nohost/plone/events/embed.js';
        s.async = true;
        window.topic_options = (window.topic_options || []).concat([ { 
            element_id: 'embeded_id',
            elements_length: 5, //how many elements to show
            embed_css: true, //embed rt.topicembed css styles
            new_window: true //open links in new window
        }]);
        document.body.appendChild(s);
    }());
</script>
```


This code can be later embeded on the external site, the same as **twitter** widget.

Output
------

The template for rendering the output is registered by this ZCML slug:

```xml
    <browser:page
         name="json"
         for="Products.ATContentTypes.interfaces.topic.IATTopic"
         layer="..interfaces.IBrowserLayer"
         class=".embed.EmbedJSON"
         permission="zope2.View"
     />
```
and it's called `items_macro.pt`. It generates an HTML output similar to:

```html
<div>
   <p>
     <a href="http://nohost/plone/events/event1">Event 1 title</a>
   </p>
   <div>Short event description</div>
   <img src="http://nohost/plone/events/event1/image_mini" title="Event 1 image">
</div>
<div>
   <p>
     <a href="http://nohost/plone/events/event2">Event 2 title</a>
   </p>
   <div>Other event description</div>
   <img src="http://nohost/plone/events/event2/image_mini" title="Event 2 image">
</div>
```


