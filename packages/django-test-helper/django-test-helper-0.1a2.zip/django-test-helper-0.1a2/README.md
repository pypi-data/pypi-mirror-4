Django Test Helper
==================

Django Test Helper provides some utility functions when testing Django applications

Installation
------------

Run `pip install django-test-helper`

Helpers
-------

###authenticated_client
A context that provides a Django test Client instance with an authenticated user. It takes a username and a password as arguments.

```python
from django.test import TestCase
from test_helper.utils import authenticated_user
from django.core.urlresolvers import reverse

class MyTest(TestCase):
    def test_protected_view(self):
        with autenticated_user('username', 'pass') as client:
            response = client.get(reverse('protected_view')
            self.assertEqual(response.status, 200)
```

###image_file
Creates on-the-fly an image and returns it. It takes a size tuple and a color rgb tuple.

```python
from django.test import TestCase
from test_helper.utils import image_file

class MyTest(TestCase):
    def test_form(self):
        data = {
            'first_name': 'John',
            'last_name': 'Smith',
        }
        image = image_file(size=(100, 100),
                           color=(128, 128, 128))
        files = {
            'avatar': image,
        }
        form = ProfileForm(data, files)
        self.assertTrue(form.is_valid())
```