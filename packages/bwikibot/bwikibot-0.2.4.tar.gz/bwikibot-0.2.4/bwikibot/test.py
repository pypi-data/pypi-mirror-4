from datetime import datetime
from unittest import TestCase, main

from .api import datetime2zulu, zulu2datetime

class Zulu(TestCase):
    def test_now(self):
        now = datetime.now().replace(microsecond=0)
        zulu = datetime2zulu(now)

        self.assertEqual(zulu2datetime(zulu), now)


if __name__=='__main__':
    main()
