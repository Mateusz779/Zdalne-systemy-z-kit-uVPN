class Image:
    def __init__(self, id, token, name):
        self.id = id
        self.name = name
        self.token = token

class ImageManager:
    def __init__(self):
        self.images = []

    def add_image(self, machine):
        self.images.append(machine)

    def remove_image(self, machine):
        self.images.remove(machine)

    def get_image_by_token(self, token):
        for image in self.images:
            if image.token == token:
                return image
        return None
