from django.utils import unittest

from geetar.paginator import WindowedPaginator, WindowedPage


class WindowedPaginatorTestCase(unittest.TestCase):
    
    def test_windowed_paginator(self):

        items = range(0, 86)
        pager = WindowedPaginator(items, 5) # 86 objects, 18 pages

        # ---- Odd window

        window = 5
        page = pager.page(1, 5)

        self.assertIsInstance(page, WindowedPage)

        # Test sets by window size, then a tuple: index 0 is pages that should equate to the page range in index 1

        test_sets = {
            4: (
                ([1,2], [1, 2, 3, 4, 5, None, 18],), # Lower end
                ([6], [1, None, 5, 6, 7, 8, None, 18],), # Middle
                ([16, 17, 18], [1, None, 14, 15, 16, 17, 18],), # Higher
            ),
            5: (
                ([1, 2, 3], [1, 2, 3, 4, 5, 6, None, 18],), # Lower end
                ([5], [1, None, 3, 4, 5, 6, 7, None, 18],), # Middle
                ([16, 17, 18], [1, None, 13, 14, 15, 16, 17, 18]) # Higher
            ),
            18: (
                (range(1, 19), range(1, 19),),
            )
        }

        for window in test_sets.keys():
            for test in test_sets[window]:
                for num in test[0]:
                    page = pager.page(num, window=window)
                    self.assertIsInstance(page, WindowedPage, 'Instance is not a `WindowedPage` object')
                    self.assertEqual(page.page_range, test[1], 'Window %d, page %d page range incorrect' % (window, num))