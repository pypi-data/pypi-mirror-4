import unittest
from rbase.base import Base

class BaseTests(unittest.TestCase):

    def tearDown(self):
        Base.clear()

    def test_all(self):
        for i in range(10):
            item = Base(i)
            item.save()
        self.assertEquals(len(Base.all()), 10)

    def test_get(self):
        item = Base('ident')
        self.assertEquals(Base.get('ident'), None)
        item.save()
        self.assertEquals(Base.get('ident').ident, 'ident')

    def test_exists(self):
        item = Base('ident')
        self.assertFalse(Base.exists(item))
        item.save()
        self.assertTrue(Base.exists(item))

    def test_make_key(self):
        item = Base('ident')
        self.assertEquals(item.redis_key, 'Base:ident')

    def test_update(self):
        item = Base('ident', object_id='object_id')
        item.save()
        item.object_id = 'different_object_id'
        item.update()
        self.assertEquals(item.object_id, 'object_id')

    def test_delete(self):
        item = Base('ident')
        item.save()
        item.delete()
        self.assertFalse(Base.get('ident'))

if __name__ == '__main__':
    unittest.main()
