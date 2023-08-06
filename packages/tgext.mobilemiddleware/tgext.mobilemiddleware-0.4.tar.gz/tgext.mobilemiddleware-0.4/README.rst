About Mobile Middleware
-------------------------

Mobile Middleware is a middleware for WSGI applications.

Thought to be used on TurboGears 2 applications it detects mobile browser and provides a way
to detect and react to them. Detection expression can be customized and action can
change from plain detection to exposing a specific custom template for mobile requests

You will be able to see if your request is coming from a mobile browser with::

    from tg import request
    request.is_mobile

Installing
-------------------------------

tgext.mobilemiddleware can be installed both from pypi or from bitbucket::

    easy_install tgext.mobilemiddleware

should just work for most of the users

Enabling Mobile Agents Detection
----------------------------------

In your application *config/middleware.py* import **MobileMiddleware**:: 

    from tgext.mobilemiddleware import MobileMiddleware

Change your **make_app** method::

    app = make_base_app(global_conf, full_stack=True, **app_conf)
    return MobileMiddleware(app, app_conf)

Exposing Mobile Templates
----------------------------

**tgext.mobilemiddleware** implements a *@expose_mobile* decorator that works like *@expose*
TurboGears2 decorator which can be used to specify which template to expose for mobile requests.

This will work by switching the template before rendering the view if the request
is detected to be from a mobile browser.
*@expose_mobile* supports the same template naming convention that @expose uses
and can accept any rendering engine that has been registered in TurboGears
by specifying it as *engine:module.template_name* 

Examples::

    @expose('app.templates.index')
    @expose_mobile('app.templates.mobile.index')
    def index(self, *args, **kw):
        return dict()


Customizing User Agents Detection
-----------------------------------

If you want to quickly customize the regular expression used to detect the mobile browser you can define *mobile.agents* 
configuration variable in your application config file and set it to the regular expression that you want to use.

For more complex customizations, you may create your own subclass of **DetectMobileBrowser**, 
or callable object and supply it as an argument to **MobileMiddleware**, like::

    return MobileMiddleware(app, app_conf, mobile_browser_detector=YourClass)

**DetectMobileBrowser** behaviour can be changed by any subclass by overridding the **DetectMobileBrowser.perform_detection** method.
If user has defined a custom regular expression it will be available inside the *perform_detection* method as *self.custom_mobile_re*
