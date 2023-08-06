from services import StatusObject as Base


class StatusObject(Base):

    def test_cache(self):
        self.cache = True

    def test_db(self):
        self.db = True

    def test_settings(self):
        self.settings = True
