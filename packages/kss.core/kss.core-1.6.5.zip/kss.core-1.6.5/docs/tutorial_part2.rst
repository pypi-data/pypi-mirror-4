This tutorial is the direct continuation of the `first part`_.  We will
learn how to specify server side actions and finally complete our first useful
AJAX example.

.. _first part: http://kukit.org/documentation/tutorials/begin-with-kss

Creating a server action
------------------------

Until now, we called a client action (alert) from our event. This was good to
test if our event was triggered. However, in a typical AJAX pattern, we want to
call a server action.

Server actions are implemented as methods on the server. They could be any kind
of callable methods, including python scripts, and this is what we will do
first. Besides doing whatever is necessary for the business
logic, the task of the server method is to assemble a sequence of commands.
These commands are marshalled back to the client to be executed there. A
command is a call to DOM manipulation client code. A command can (in most
cases, should) have a selector, to set the scope of nodes on which the command
is executed, and a set of parameters for execution.

Although existing components come with implemented server action methods, it is
easy to create a custom one since it requires only python skills. Let's create
a python script (`response1`) in the custom skin :

::

        # import Through-The-Web(TTW) API
        from kss.core.ttwapi import startKSSCommands
        from kss.core.ttwapi import getKSSCommandSet
        from kss.core.ttwapi import renderKSSCommands

        # start a view for commands
        startKSSCommands(context, context.REQUEST)

        # add a command
        core = getKSSCommandSet('core')
        core.replaceInnerHTML('#portal-siteactions', '<h1>We did it!</h1>')

        # render the commands
        return renderKSSCommands()

After the imports, we initialize the view that will hold the KSS commands that
we want to send back to the client.

Then we add a command. The name of the command is `replaceInnerHTML`. This is
one of our most useful commands : it simply replaces the contents of the
selected html nodes with some html string.

To specify which nodes will be selected, the command also needs a selector: in
this example, a standard CSS selector.  We choose to replace the portal actions
of a Plone portal that are on the top of the page - but we could choose any
other element as well.

The `replaceInnerHTML` method is accessed through a command set. Since we have
a pluggable system, we need to refer to the component that defines the methods,
in this case, the `'core'` command set.

In the last line, the `renderKSSCommands` call is mandatory : it will generate
the response payload from the accumulated commands. To look at this payload,
let's access this method directly from the browser : 
`http://localhost:8080/plone/front-page/response1`.
We will see "We did it!" on the screen, but let's have a more careful look at
the source of the response :

::
        <?xml version="1.0" ?>
        <kukit xmlns="http://www.kukit.org/commands/1.0"
            xmlns:tal="http://xml.zope.org/namespaces/tal"
            xmlns:metal="http://xml.zope.org/namespaces/metal">
        <commands>
        <command selector="#portal-siteactions"
                       name="replaceInnerHTML" selectorType="">
            <param name="html"><![CDATA[<h1>We did it!</h1>]]></param>
        </command>
        </commands>
        </kukit><

This is an XML response, where we can see how commands and parameters are
actually marshalled. When the response is interpreted by the kss engine, it
will execute the commands with the given parameters.

Calling the server action
-------------------------

Now, we have finished to build our server action; we want to call it from our
kss style sheet.  We replace our previous kss event rule with the following
one :

::

        a.navTreeCurrentItem:click {
            evt-click-preventdefault: True;
            action-server: response1;
        }

The `action-server` line specifies the name of the remote method to call :
`response1` (since this is how we named our python script). The script will be
called on the context url of the page we are at.

Let's reload the page so that the new kss comes into effect. Open the
loggingpane. Then press the "Home" line in the navtree portlet. It works! We
can see the site actions replaced with our text.  Also notice that a few things
have been logged to the loggingpane :

::
        
        ...
        DEBUG: RequestManager Notify server http://localhost:8080/plone/front-page/response1, rid=0 (RQ: 1 OUT, 0 WAI)
        DEBUG: RequestManager Received result with rid=0 (RQ: 0 OUT, 0 WAI)
        INFO: Parse commands
        DEBUG: Number of commands: 1
        DEBUG: Selector type: default (css), selector : "#portal-siteactions", selected nodes:1
        DEBUG: Command Name: replaceInnerHTML
        ...

This gives a lot of information about what happened in the client :

- the server is notified,
- the response is received,
- it is parsed successfully,
- it contains one command,
- the command selects 1 node to act on. 

Now let's change our command response in the following way :

::

        ...
        from DateTime import DateTime

        # add a command
        core = getKSSCommandSet('core')
        content = '<h1>We did it!</h1><span>%s</span>' % DateTime()
        core.replaceInnerHTML('#portal-siteactions', content)
        ...

This way, the current time is sent back by the server on each click and we can
see that something happens.

It is interesting to note that we did not need to reload the page in order to
see the effect of this change. Because we only made changes on the server, we
did not need to load anything new on the client side. So we can continue to
debug from the already loaded page and this will work even through server
restarts.

What happens if the server-side script has an error, or the client does not get
a correct response for some reason ? In this case, we will see this in the
loggingpane :

::

        DEBUG: RequestManager Notify server http://localhost:8080/tutorial/front-page/response1, rid=3 (RQ: 1 OUT, 0 WAI)
        DEBUG: RequestManager Received result with rid=3 (RQ: 0 OUT, 0 WAI)
        ERROR: Request failed at url http://localhost:8080/tutorial/front-page/response1, rid=3

The error `Request failed` indicates that we have to turn to the server to
debug the problem. Our best friend, the zope error log will tell us about the
actual problem.

Server action parameters
------------------------

Like client actions, server actions can also accept parameters. The parameters
will be sent to the server as form variables. Zope publisher can then pass them
as usual keyword parameters to our python script. Let's render a parameter
coming from the client. We add parameter `mymessage` to the python script. Then
modify the script :

::
 
        ... 
        # add a command
        core = getKSSCommandSet('core')
        content = '<h1>We did it!</h1><span><b>%s</b> at %s</span>' % (mymessage, DateTime()))
        core.replaceInnerHTML('#portal-siteactions', content)
        ...


We modify our kss rule to actually send the parameter from the client :

::

        a.navTreeCurrentItem:click {
            evt-click-preventdefault: True;
            action-server: response1;
            response1-mymessage: "Hello Plone!";
        }

The key `response1-mymessage` is built identically to how we did it with the
client action.  We use the name of the action first and then, following the
dash, the name of the parameter.  This time, because we change the stylesheet,
we need to reload the page before testing by clicking on the bound node.

To understand better how all this is working, let's enter a second rule in the
kss :

::

        ul#portal-globalnav li a:click {
            evt-click-preventdefault: True;
            action-server: response1;
            response1-mymessage: "clicked on global nav";
        }

This shows some new things. First, you can see that you can use any css
selector in a rule. In this case, the selector will select all globalnav tab
links. If you reload the page, you will notice that if you click on any of
those links, different content is replaced because different parameter are
passed to the server.

If you take a look at the loggingpane after the page reload, you can see
something like this :

::

        INFO: Initializing kss
        ...
        INFO: Count of KSS links: 1
        INFO: Start loading and processing http://localhost:8080/plone/portal_css/Plone%20Default/tutor-cachekey9967.kss resource type kss
        DEBUG: EventRule #0: a.navTreeCurrentItem EVENT=click
        DEBUG: EventRule #1: ul#portal-globalnav li a EVENT=click
        INFO: Finished loading and processing http://localhost:8080/plone/portal_css/Plone%20Default/tutor-cachekey9967.kss resource type kss in 35 + 29 ms
        INFO: Starting setting up events for document
        DEBUG: EventRule #0 mergeid @@0@@click selected 1 nodes
        DEBUG: EventRule #1 mergeid @@0@@click selected 4 nodes
        DEBUG: Binding 0 special rules in grand total
        DEBUG: instantiating event id=@@0, classname=0, namespace=null
        DEBUG: Binding to 5 nodes in grand total
        ...

This shows that the second rule is also in effect now. Moreover, it has
selected 4 nodes (or however many globalnav tabs you have). A lot of other
information is also logged, it should not worry you at the moment.

Different command selector
--------------------------

Until now, in our command, we used the default css selector.  It is possible to
use other types of selectors, like a html id selector. Let's modify our command
in the following way :

::
        
        ... 
        # add a command
        core = getKSSCommandSet('core')
        content = '<h1>We did it!</h1><span><b>%s</b> at %s</span>' % (mymessage, DateTime()))
        selector = core.getHtmlIdSelector('portal-personaltools'),
        core.replaceInnerHTML(selector, content)
        ...

What an HTML id selector selects should be obvious. Reload the page and
exercise...

Commands can also select multiple nodes :

::

        ... 
        # add a command
        core = getKSSCommandSet('core')
        content = '<h1>We did it!</h1><span><b>%s</b> at %s</span>' % (mymessage, DateTime()))
        selector = core.getCssSelector('dt.portletHeader a'),
        core.replaceInnerHTML(selector, content)
        ...

The css selector `dt.portletHeader a` selects all portlet headers in the page,
so the replacement will be executed not on one node but on many nodes (as can
also be seen in the loggingpane). Try clicking the `Home` link in the navtree,
or any of the globalnav tabs to see the effect.

You can also add multiple commands : each of them will be executed, in the
order they have within the payload.

One thing is important to note. If a command selects no nodes, it is not an
error : the behaviour designed in this case is that nothing happens. This is in
line with the usual logic of css selectors in style sheets.

Using a different event
-----------------------

So far we have only used the `click` event: let's try with another one,
`timeout`. The `timeout` event does not directly map to a browser event but it
is a (conceptual) kss event. This shows that in kss anything can be an event
and how an event binds itself is freely implementable.

Let's add the following rule to the end of our kss file (altogether we will
have 3 rules then) :

::

        document:timeout {
            evt-timeout-delay: 8000;
            action-server: response1;
            response1-mymessage: "from timeout";
        }

The `timeout` event implements a recurring timeout tick. It has a `delay`
parameter that specifies the time in milliseconds. In this case, the event will
be triggered each 8 seconds over and over again. The event calls the server
action that we already have but with a different parameter.

The `timeout` event does not really need a node as binding scope. This is why
we use `document` instead of a css selector as we did until now. This is a
special kss selector that is an extension to css and simply means : bind this
event exactly once when the document loads, with a scope of no nodes but the
document itself.

If you reload the page you will notice that clicks work as before, however, 
every 8 seconds, the timeout event will trigger and do a replacement on the
required nodes.

There are some more advanced issues that this example opens and we will show
more about them in the next tutorials.

*Congratulations!*

You have completed your first kss tutorial, learned the basics and now you are
able to start some experimentation on your own. Or, just sit back and relax.

Server-side commands - the zope3 way
------------------------------------

A python script may not be the most proper implementation of a server method.
Plone community is moving towards zope3 style development : the suggested way
is to use a browser view (multiadapter). Previously, you have created a demo
product, now create a python module `demoview.py` in the product root directory
on the filesystem :

::

        from kss.core import KSSView
        from datetime import datetime

        class DemoView(KSSView):

            def response1(self, mymessage):
                # build HTML
                content = '<h1>We did it!</h1><p><b>%s</b> at %s</p>'
                date = str(datetime.now()) 
                content = content % (mymessage, date)       
                
                # KSS specific calls
                core = self.getCommandSet('core')
                core.replaceInnerHTML('#portal-siteactions', content)
                return self.render()

We inherit our view from `KSSView`. It inherits from Five's `BrowserView`. 

It is maybe time to explain how the `ttwapi` uses those views.

- `startKSSCommands` does the instantiation of a `KSSView`.
- `getKSSCommandSet` is the call equivalent to `self.getCommandSet`.
- `renderKSSCommands` calls `self.render`.

To be able to use the method, you need to add the following to your
`configure.zcml` file :

::

         <browser:page
              for="plone.app.kss.interfaces.IPortalObject"
              class=".demoview.DemoView"
              attribute="response1"
              name="response1"
              permission="zope2.View"
              />

The interface that the view is bound to is one setup by `kss.core` on all
portal objects. You could also use directly the interfaces defined by Plone 2.5
directly, however that would not work on Plone 2.1 so we offer a few "wrapper
interfaces" like the one in this example.

If you still have the `response1` python script from the begin of this
tutorial, do not forget to rename it.  Now it is time to restart Zope.  If
everything goes well, the page functions as previously but you can see from the
replacement message that the new method is operating on your page.

Remember, when you are working with browser views, you must restart Zope each
time you want to test the changes made in the view code.

