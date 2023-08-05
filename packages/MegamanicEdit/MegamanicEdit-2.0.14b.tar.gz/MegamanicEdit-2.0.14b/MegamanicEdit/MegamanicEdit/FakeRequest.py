class FakeRequest:

    __allow_access_to_unprotected_subobjects__ = True

    def __init__(self):
        self.form = {}

    def set(self, key, value):
        self.form[key] = value
