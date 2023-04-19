import unittest
import os

from mmisp.process import run

class TestMyFunction(unittest.TestCase):
    def test_rename(self):
        test_file = 'test.txt'
        with open(test_file, 'w') as f:
            f.write('test')

        run(test_file, [{'step': 'move', 'output': test_file + '.new'}])
        self.assertFalse(os.path.isfile(test_file))
        self.assertTrue(os.path.isfile(test_file + '.new'))

        os.remove(test_file + '.new')

    def test_del(self):
        test_file = 'test.txt'
        with open(test_file, 'w') as f:
            f.write('test')

        run(test_file, [{'step': 'del'}])
        self.assertFalse(os.path.isfile(test_file))

if __name__ == '__main__':
    unittest.main()
