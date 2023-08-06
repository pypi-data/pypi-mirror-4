Tumblpy
=======


Tumblpy is a Python library to help interface with `Tumblr v2 REST API <http://www.tumblr.com/docs/en/api/v2>`_ & OAuth

Features
--------

* Retrieve user information and blog information
* Common Tumblr methods
   - Posting blog posts
   - Unfollowing/following blogs
   - Edit/delete/reblog posts
   - And many more!!
* Photo Uploading


Installation
------------

Installing Tumbply is simple: ::

    $ pip install python-tumblpy


Usage
-----

Authorization URL
~~~~~~~~~~~~~~~~~
::

    # Without a dynamic callback url
    # This will use the callback url specified in your app

    # Go to http://www.tumblr.com/oauth/apps and click your
    # app to find out your dynamic callback url
    t = Tumblpy(app_key = '*your app key*',
                app_secret = '*your app secret*')

If you wish to have a dynamic callback url, specify ``callback_url`` when you initiate the class.

::

    t = Tumblpy(app_key = '*your app key*',
            app_secret = '*your app secret*',
            callback_url = 'http://example.com/callback/')

::

    auth_props = t.get_authentication_tokens()
    auth_url = auth_props['auth_url']
    
    oauth_token = auth_props['oauth_token']
    oauth_token_secret = auth_props['oauth_token_secret']
    
    Connect with Tumblr via: % auth_url

Once you click "Allow" be sure that there is a URL set up to handle getting finalized tokens and possibly adding them to your database to use their information at a later date.

Handling the Callback
~~~~~~~~~~~~~~~~~~~~~
::

    # oauth_token and oauth_token_secret come from the previous step
    # if needed, store those in a session variable or something

    t = Tumblpy(app_key = '*your app key*',
            app_secret = '*your app secret*',
            oauth_token=oauth_token,
            oauth_token_secret=oauth_token_secret)

    # In Django, you'd do something like
    # oauth_verifier = request.GET.get('oauth_verifier')
    
    # or get the oauth_verifier by visiting auth_url in a browser
    # after you authorize the app you'll be redirected to a page (your oauth_callback or Tumblr's 404)
    # grab the oauth_verifier from the url of that page

    oauth_verifier = *Grab oauth verifier from URL*
    authorized_tokens = t.get_authorized_tokens(oauth_verifier)
    
    final_oauth_token = authorized_tokens['oauth_token']
    final_oauth_token_secret = authorized_tokens['oauth_token_secret']
    
    # Save those tokens to the database for a later use?

Getting some User information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    # Get the final tokens from the database or wherever you have them stored

    t = Tumblpy(app_key = '*your app key*',
                app_secret = '*your app secret*',
                oauth_token=final_tokens['oauth_token'],
                oauth_token_secret=final_tokens['oauth_token_secret'])

    # Print out the user info, let's get the first blog url...
    blog_url = t.post('user/info')
    blog_url = blog_url['user']['blogs'][0]['url']

Get a User Avatar URL (No need for authentication for this method)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    t = Tumblpy()
    avatar = t.get_avatar_url(blog_url='omglegit.tumblr.com', size=128)
    print avatar['url']

    # OR

    avatar = t.get('avatar', blog_url='omglegit.tumblr.com'. extra_endpoints=['128'])
    print avatar['url']

Getting posts from a certain blog
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    # Assume you are using the blog_url and Tumblpy instance from the previous section
    posts = t.get('posts', blog_url=blog_url)
    print posts

Creating a post with a photo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    # Assume you are using the blog_url and Tumblpy instance from the previous sections

    photo = open('/path/to/file/image.png', 'rb')
    post = t.post('post', blog_url=blog_url, params={'type':'photo', 'caption': 'Test Caption', 'data': photo})
    print post  # returns id if posted successfully

Posting an Edited Photo *(This example resizes a photo)*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    # Assume you are using the blog_url and Tumblpy instance from the previous sections

    # Like I said in the previous section, you can pass any object that has a
    # read() method

    # Assume you are working with a JPEG

    from PIL import Image
    from StringIO import StringIO

    photo = Image.open('/path/to/file/image.jpg')

    basewidth = 320
    wpercent = (basewidth / float(photo.size[0]))
    height = int((float(photo.size[1]) * float(wpercent)))
    photo = photo.resize((basewidth, height), Image.ANTIALIAS)

    image_io = StringIO.StringIO()
    photo.save(image_io, format='JPEG')
    
    image_io.seek(0)

    try:
        post = t.post('post', blog_url=blog_url, params={'type':'photo', 'caption': 'Test Caption', 'data': photo})
        print post
    except TumblpyError, e:
        # Maybe the file was invalid?
        print e.message

Following a user
~~~~~~~~~~~~~~~~
::

    # Assume you are using the blog_url and Tumblpy instance from the previous sections
    try:
        follow = t.post('user/follow', params={'url': 'omglegit.tumblr.com'})
    except TumblpyError:
        # if the url given in params is not valid,
        # Tumblr will respond with a 404 and Tumblpy will raise a TumblpyError

Catching errors
~~~~~~~~~~~~~~~
::

    try:
        t.post('user/info')
    except TumbplyError, e:
        print e.message
        print 'Something bad happened :('
