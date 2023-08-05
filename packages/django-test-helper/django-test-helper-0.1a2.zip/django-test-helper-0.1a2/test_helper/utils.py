from django.test.client import Client
try:
    from PIL import Image
except:
    import Image
from StringIO import StringIO


class authenticated_client(object):
    def __init__(self, username, password):
        self.client = Client()
        self.username = username
        self.password = password

    def __enter__(self):
        self.client.login(username=self.username, password=self.password)
        return self.client

    def __exit__(self, type, value, traceback):
        self.client.logout()


def image_file(size=(50, 50), color=(256, 0, 0)):
    file = StringIO()
    image = Image.new("RGBA", size, color)
    image.save(file, 'png')
    file.name = 'test.png'
    file.seek(0)
    return file
