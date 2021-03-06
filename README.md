# dictshield-views
dictshield-views provides data transformations on DictShield objects.
## TL;DR (Show me the code!)

```python
    from dictshield.documents import Document
    from dictshield.views import View

    class Public(WhitelistView):
     fields = ['name', 'body']

    class Post(Document):
     name = StringField()
     body = StringField()
     username = StringField()
     password = PasswordField()

    >>> entry = Post(**{'name':'1', 'body':'2', 'username':'3', 'password':'4'})
    >>> entry.name
    '1'
    >>> entry.password
    '4'
    >>> Public(entry).name
    '1'
    >>> Public(entry).password
    AttributeError: 'Public' doesn't contain the attribute 'entry'
```

## Definitions
- DictShield, a modeling layer to serve as transport from python dicts
  to objects. https://github.com/j2labs/dictshield

- Brubeck, a Python web-framework built behind the mogrel2 web server.
  It is the primary public consumer of DictShield. https://github.com/j2labs/brubeck

- GWT, a Java web framework which translates Java code into HTML, CSS
  and javascript for rich client apps. http://code.google.com/webtoolkit/

## Background
The idea for dictshield-views came from a discussion on brubeck-dev. James
Dennis was thinking of how to represent permissioning on a per-field
basis for DictShield Documents. The concept of whitelisting and
blacklisting fields came up, which reminded me of data transformations
provided by GWT's RequestFactory proxies. With these proxies, you can
transform your server-side representation of an object to a smaller
view (akin to database views) in order to minimize transportation
costs.

## Overview
dictshield-views provides `View` objects, which allow you to customize the
representation of the original object. Views can be though of in two
major groups: restrictive views or transformational views.

A great example of a restrictive view is a field white or
black list. Given the object:

```python
    from dictshield.document import Document
    from dictshield.fields import StringField

    class User(Document):
      username = StringField();
      full_name = StringField();
      password = PasswordField();
      bio = StringField();
```

When we serialize this a client app, we may want to strip out some
data so it isn't leaked (such as their password).

```python
    class PublicView(RestrictiveView):
        blacklist=['password']
```

This is an example view which blacklists access to the password field.
You can instantiate these views with a Document that at least has a
password field. Access to all other fields acts as normal, but when
requesting a field under restriction, an exception is raised.

```python
    >>> user = User(**{'username':'justinlilly',
    ...   'full_name':'Justin Lilly',
    ...   'password':'s3cur3!',
    ...   'bio': 'Born, now just trying to survive.'})
    >>> public_user = PublicView(user)
    >>> user.password
    "s3cur3!"
    >>> public_user.password
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    AttributeError: 'PublicView' object has no attribute 'password'
```

The other main type of views are transformative views. These views
serve to alter the content of the underlying Document. A fun example
of this might be a pirate speak view, but more serious versions might
be a curse word filter, a view which will on-the-fly scale images into
a scaled down size or compositing multiple fields into a synthetic
field.


```python
    class PirateSpeak(TransformativeView):
      transformable=['bio', 'full_name']

      def transform(self, field_name, value):
        if field_name == 'full_name':
          names = value.split()
          names[-1] = "Blackbeard"
          value = ' '.join(names)
        elif field_name == 'bio':
          value = pirateify(value)
        return value
```


## How it works
`RestrictiveView` works by overriding the `__getattr__()` method. In
the case of a whitelist, if the requested attribute isn't in the set
of fields in the white list, an AttributeError is raised. If it is in
the set, the call is proxied back to the instance of the Document.

`TransformativeView` is a bit different. When you attempt to get the
backing attribute of the Document underlying the view, it is run
through processing (assuming the attribute is in the `transformable`
list), and the result is returned. The `transform` method is given a
copy of the value from the underlying value.

## Concerns
My biggest concern here is that you could build arbitrarily long
chains of these views, which could cause a performance problem if each
of them is just proxying back to the previous one to get an attribute.
I haven't done much thinking as to how this could be mitigated, but
doesn't seem untractable.

## References
- DictShield https://github.com/j2labs/dictshield
- GWT RequestFactory Proxies http://code.google.com/webtoolkit/doc/latest/DevGuideRequestFactory.html#proxies

## TODOs
- TODO(justinlilly): Does requiring the backing model to have a
  password field matter? Should we just override getattr and if its
  password, blow up, otherwise let python handle it?

- TODO(justinlilly): When you request a blacklisted field, should you
  get an exception, or a simple "doesn't exist, sorry" result?

- TODO(justinlilly): How important is composeability with these Views?

- TODO(justinlilly): Should TransformativeView do convention over
  configuration and make transform_bio(value) be for the bio call? I
  think I like that a bit better. Could also likely remove the
  transformable list.
