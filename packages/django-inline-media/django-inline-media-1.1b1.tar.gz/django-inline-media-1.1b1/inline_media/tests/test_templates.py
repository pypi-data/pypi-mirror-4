#-*- coding: utf-8
try:
    from BeautifulSoup import BeautifulSoup, NavigableString
except ImportError:
    from beautifulsoup import BeautifulSoup, NavigableString

from django.template import TemplateSyntaxError
from django.test import TestCase as DjangoTestCase

from inline_media.models import PictureSet
from inline_media.parser import inlines
from inline_media.tests.test_models import (create_picture_1, 
                                            create_picture_2,
                                            create_picture_3)


class PictureTemplateTestCase(DjangoTestCase):
    """Test all combination of templates and Picture options.

    There are 3 templates for 5 sizes (mini, small, medium, large, full) and
    a few Picture options (show_as_link, show_description_inline, show_author,
    show_license).
    """
    def setUp(self):
        self.picture = create_picture_1()
        self.tag = (u'<inline type="inline_media.picture" '
                    u'id="%d"' % self.picture.id + u' class="%s"/>')

    def _reverse_default_boolean_field_values(self):
        self.picture.show_as_link = False
        self.picture.show_description_inline = False
        self.picture.show_author = True
        self.picture.show_license = True
        self.picture.save()

    def test_mini_with_default_options(self):
        tmpl = 'inline_media/inline_media.picture.mini.html'
        positions = ['inline_mini_left', 'inline_mini_right']
        for cssclass in positions:
            html = inlines(self.tag % cssclass, return_list=False)
            self.assertTemplateUsed(html, tmpl)
            # default options:
            #  - show_as_link = True
            #  - show_description_inline = True
            #  - show_author = False
            #  - show_license = False
            # But! template for size 'mini' never includes 
            # picture's author, license or description
            soup = BeautifulSoup(html)
            links = soup.findAll('a', attrs={'class': 'picture'})
            self.assert_(len(links) == 1)
            self.assert_(html.find('inline_description') == -1)
            self.assert_(html.find('inline_author') == -1)
            self.assert_(html.find('inline_license') == -1)

    def test_small_with_default_options(self):
        tmpl = 'inline_media/inline_media.picture.default.html'
        positions = ['inline_small_left', 'inline_small_right']
        for cssclass in positions:
            html = inlines(self.tag % cssclass, return_list=False)
            self.assertTemplateUsed(html, tmpl)
            # default options:
            #  - show_as_link = True
            #  - show_description_inline = True
            #  - show_author = False
            #  - show_license = False
            soup = BeautifulSoup(html)
            links = soup.findAll('a', attrs={'class':'picture'})
            self.assert_(len(links) == 1)
            descrip = soup.findAll('p', attrs={'class':'inline_description'})
            self.assert_(len(descrip) == 1)
            self.assert_(html.find('inline_author') == -1)
            self.assert_(html.find('inline_license') == -1)

    def test_medium_with_default_options(self):
        tmpl = 'inline_media/inline_media.picture.default.html'
        positions = ['inline_medium_left', 'inline_medium_right']
        for cssclass in positions:
            html = inlines(self.tag % cssclass, return_list=False)
            self.assertTemplateUsed(html, tmpl)
            # default options:
            #  - show_as_link = True
            #  - show_description_inline = True
            #  - show_author = False
            #  - show_license = False
            soup = BeautifulSoup(html)
            links = soup.findAll('a', attrs={'class':'picture'})
            self.assert_(len(links) == 1)
            descrip = soup.findAll('p', attrs={'class':'inline_description'})
            self.assert_(len(descrip) == 1)
            self.assert_(html.find('inline_author') == -1)
            self.assert_(html.find('inline_license') == -1)

    def test_large_with_default_options(self):
        tmpl = 'inline_media/inline_media.picture.default.html'
        positions = ['inline_large_left', 'inline_large_right']
        for cssclass in positions:
            html = inlines(self.tag % cssclass, return_list=False)
            self.assertTemplateUsed(html, tmpl)
            # default options:
            #  - show_as_link = True
            #  - show_description_inline = True
            #  - show_author = False
            #  - show_license = False
            soup = BeautifulSoup(html)
            links = soup.findAll('a', attrs={'class':'picture'})
            self.assert_(len(links) == 1)
            descrip = soup.findAll('p', attrs={'class':'inline_description'})
            self.assert_(len(descrip) == 1)
            self.assert_(html.find('inline_author') == -1)
            self.assert_(html.find('inline_license') == -1)

    def test_full_with_default_options(self):
        tmpl = 'inline_media/inline_media.picture.full.html'
        positions = ['inline_full_left', 
                     'inline_full_center', 
                     'inline_full_right']
        for cssclass in positions:
            html = inlines(self.tag % cssclass, return_list=False)
            self.assertTemplateUsed(html, tmpl)
            # default options:
            #  - show_as_link = True
            #  - show_description_inline = True
            #  - show_author = False
            #  - show_license = False
            soup = BeautifulSoup(html)
            links = soup.findAll('a', attrs={'class':'picture'})
            self.assert_(len(links) == 0) # no link in full mode
            descrip = soup.findAll('p', attrs={'class':'inline_description'})
            self.assert_(len(descrip) == 1)
            self.assert_(html.find('inline_author') == -1)
            self.assert_(html.find('inline_license') == -1)

    def test_mini_with_reversed_default_options(self):
        tmpl = 'inline_media/inline_media.picture.mini.html'
        positions = ['inline_mini_left', 'inline_mini_right']
        self._reverse_default_boolean_field_values()
        for cssclass in positions:
            html = inlines(self.tag % cssclass, return_list=False)
            self.assertTemplateUsed(html, tmpl)
            # reversed default options:
            #  - show_as_link = False
            #  - show_description_inline = False
            #  - show_author = False
            #  - show_license = False
            # But! template for size 'mini' never includes 
            # picture's author, license or description
            soup = BeautifulSoup(html)
            links = soup.findAll('a', attrs={'class': 'picture'})
            self.assert_(len(links) == 0)
            self.assert_(html.find('inline_description') == -1)
            self.assert_(html.find('inline_author') == -1)
            self.assert_(html.find('inline_license') == -1)

    def test_small_with_reversed_default_options(self):
        tmpl = 'inline_media/inline_media.picture.default.html'
        positions = ['inline_small_left', 'inline_small_right']
        self._reverse_default_boolean_field_values()
        for cssclass in positions:
            html = inlines(self.tag % cssclass, return_list=False)
            self.assertTemplateUsed(html, tmpl)
            # reversed default options:
            #  - show_as_link = False
            #  - show_description_inline = False
            #  - show_author = True
            #  - show_license = True
            soup = BeautifulSoup(html)
            links = soup.findAll('a', attrs={'class':'picture'})
            self.assert_(len(links) == 0)
            self.assert_(html.find('inline_description') == -1)
            author = soup.findAll('span', attrs={'class':'inline_author'})
            self.assert_(len(author) == 1)
            license = soup.findAll('span', attrs={'class':'inline_license'})
            self.assert_(len(license) == 1)

    def test_medium_with_reversed_default_options(self):
        tmpl = 'inline_media/inline_media.picture.default.html'
        positions = ['inline_medium_left', 'inline_medium_right']
        self._reverse_default_boolean_field_values()
        for cssclass in positions:
            html = inlines(self.tag % cssclass, return_list=False)
            self.assertTemplateUsed(html, tmpl)
            # reversed default options:
            #  - show_as_link = False
            #  - show_description_inline = False
            #  - show_author = True
            #  - show_license = True
            soup = BeautifulSoup(html)
            links = soup.findAll('a', attrs={'class':'picture'})
            self.assert_(len(links) == 0)
            self.assert_(html.find('inline_description') == -1)
            author = soup.findAll('span', attrs={'class':'inline_author'})
            self.assert_(len(author) == 1)
            license = soup.findAll('span', attrs={'class':'inline_license'})
            self.assert_(len(license) == 1)

    def test_large_with_reversed_default_options(self):
        tmpl = 'inline_media/inline_media.picture.default.html'
        positions = ['inline_large_left', 'inline_large_right']
        self._reverse_default_boolean_field_values()
        for cssclass in positions:
            html = inlines(self.tag % cssclass, return_list=False)
            self.assertTemplateUsed(html, tmpl)
            # reversed default options:
            #  - show_as_link = False
            #  - show_description_inline = False
            #  - show_author = True
            #  - show_license = True
            soup = BeautifulSoup(html)
            links = soup.findAll('a', attrs={'class':'picture'})
            self.assert_(len(links) == 0)
            self.assert_(html.find('inline_description') == -1)
            author = soup.findAll('span', attrs={'class':'inline_author'})
            self.assert_(len(author) == 1)
            license = soup.findAll('span', attrs={'class':'inline_license'})
            self.assert_(len(license) == 1)

    def test_full_with_reversed_default_options(self):
        tmpl = 'inline_media/inline_media.picture.full.html'
        positions = ['inline_full_left', 
                     'inline_full_center', 
                     'inline_full_right']
        self._reverse_default_boolean_field_values()
        for cssclass in positions:
            html = inlines(self.tag % cssclass, return_list=False)
            self.assertTemplateUsed(html, tmpl)
            # reversed default options:
            #  - show_as_link = False
            #  - show_description_inline = False
            #  - show_author = True
            #  - show_license = True
            soup = BeautifulSoup(html)
            links = soup.findAll('a', attrs={'class':'picture'})
            self.assert_(len(links) == 0) # no link ever in full mode
            self.assert_(html.find('inline_description') == -1)
            author = soup.findAll('span', attrs={'class':'inline_author'})
            self.assert_(len(author) == 1)
            license = soup.findAll('span', attrs={'class':'inline_license'})
            self.assert_(len(license) == 1)


class PictureSetTemplateTestCase(DjangoTestCase):
    """Test all combination of templates and PictureSet options.

    There are 3 templates for 5 sizes (mini, small, medium, large, full) and
    a few PictureSet options (show_description_inline, show_counter).
    """
    def setUp(self):
        self.pics = create_picture_1(), create_picture_2(), create_picture_3()
        self.picset = PictureSet.objects.create(
            title="example set", slug="example-set", cover=self.pics[2], 
            order="3,1,2")
        self.picset.pictures.add(self.pics[0])
        self.picset.pictures.add(self.pics[1])
        self.picset.pictures.add(self.pics[2]) 
        self.tag = (u'<inline type="inline_media.pictureset" '
                    u'id="%d"' % self.picset.id + u' class="%s"/>')

    def _reverse_default_boolean_field_values(self):
        self.picset.show_description_inline = False
        self.picset.show_counter = True
        self.picset.save()

    def test_mini_with_default_options(self):
        # size disabled in tests.settings.INLINE_MEDIA_CUSTOM_SIZES
        tmpl = 'inline_media/inline_media.pictureset.mini.html'
        positions = ['inline_mini_left', 'inline_mini_right']
        for cssclass in positions:
            with self.assertRaises(Exception):
                html = inlines(self.tag % cssclass, return_list=False)

    def test_small_with_default_options(self):
        # size disabled in tests.settings.INLINE_MEDIA_CUSTOM_SIZES
        tmpl = 'inline_media/inline_media.pictureset.default.html'
        positions = ['inline_small_left', 'inline_small_right']
        for cssclass in positions:
            with self.assertRaises(Exception):
                html = inlines(self.tag % cssclass, return_list=False)

    def test_medium_with_default_options(self):
        tmpl = 'inline_media/inline_media.pictureset.default.html'
        positions = ['inline_medium_left', 'inline_medium_right']
        for cssclass in positions:
            html = inlines(self.tag % cssclass, return_list=False)
            self.assertTemplateUsed(html, tmpl)
            # default options:
            #  - show_description_inline = True
            #  - show_counter = False
            soup = BeautifulSoup(html)
            links = soup.findAll('a')
            self.assert_(len(links) == 3)
            # check order
            order = [int(x)-1 for x in self.picset.order.split(",")]
            for idx, link in zip(order, links):
                self.assert_(link['href'] == self.pics[idx].url)
            descrip = soup.findAll('p', attrs={'class':'inline_description'})
            self.assert_(len(descrip) == 1)
            self.assert_(html.find('inline_counter') == -1)

    def test_large_with_default_options(self):
        tmpl = 'inline_media/inline_media.pictureset.default.html'
        positions = ['inline_large_left', 'inline_large_right']
        for cssclass in positions:
            html = inlines(self.tag % cssclass, return_list=False)
            self.assertTemplateUsed(html, tmpl)
            # default options:
            #  - show_description_inline = True
            #  - show_counter = False
            soup = BeautifulSoup(html)
            links = soup.findAll('a')
            self.assert_(len(links) == 3)
            # check order
            order = [int(x)-1 for x in self.picset.order.split(",")]
            for idx, link in zip(order, links):
                self.assert_(link['href'] == self.pics[idx].url)
            descrip = soup.findAll('p', attrs={'class':'inline_description'})
            self.assert_(len(descrip) == 1)
            self.assert_(html.find('inline_counter') == -1)

    def test_full_with_default_options(self):
        tmpl = 'inline_media/inline_media.pictureset.full.html'
        positions = ['inline_full_left', 
                     'inline_full_center', 
                     'inline_full_right']
        for cssclass in positions:
            html = inlines(self.tag % cssclass, return_list=False)
            self.assertTemplateUsed(html, tmpl)
            # default options:
            #  - show_description_inline = True
            #  - show_counter = False
            soup = BeautifulSoup(html)
            links = soup.findAll('a')
            self.assert_(len(links) == 3)
            # check order
            order = [int(x)-1 for x in self.picset.order.split(",")]
            for idx, link in zip(order, links):
                self.assert_(link['href'] == self.pics[idx].url)
            descrip = soup.findAll('p', attrs={'class':'inline_description'})
            self.assert_(len(descrip) == 1)
            self.assert_(html.find('inline_counter') == -1)

    def test_mini_with_reversed_default_options(self):
        tmpl = 'inline_media/inline_media.pictureset.mini.html'
        positions = ['inline_mini_left', 'inline_mini_right']
        self._reverse_default_boolean_field_values()
        for cssclass in positions:
            with self.assertRaises(Exception):
                html = inlines(self.tag % cssclass, return_list=False)

    def test_small_with_reversed_default_options(self):
        tmpl = 'inline_media/inline_media.pictureset.default.html'
        positions = ['inline_small_left', 'inline_small_right']
        self._reverse_default_boolean_field_values()
        for cssclass in positions:
            with self.assertRaises(Exception):
                html = inlines(self.tag % cssclass, return_list=False)

    def test_medium_with_reversed_default_options(self):
        tmpl = 'inline_media/inline_media.pictureset.default.html'
        positions = ['inline_medium_left', 'inline_medium_right']
        self._reverse_default_boolean_field_values()
        for cssclass in positions:
            html = inlines(self.tag % cssclass, return_list=False)
            self.assertTemplateUsed(html, tmpl)
            # default options:
            #  - show_description_inline = False
            #  - show_counter = True
            soup = BeautifulSoup(html)
            links = soup.findAll('a')
            self.assert_(len(links) == 3)
            # check order
            order = [int(x)-1 for x in self.picset.order.split(",")]
            for idx, link in zip(order, links):
                self.assert_(link['href'] == self.pics[idx].url)
            self.assert_(html.find('inline_description') == -1)
            counter = soup.findAll('p', attrs={'class':'inline_counter'})
            self.assert_(len(counter) == 1)

    def test_large_with_reversed_default_options(self):
        tmpl = 'inline_media/inline_media.pictureset.default.html'
        positions = ['inline_large_left', 'inline_large_right']
        self._reverse_default_boolean_field_values()
        for cssclass in positions:
            html = inlines(self.tag % cssclass, return_list=False)
            self.assertTemplateUsed(html, tmpl)
            # default options:
            #  - show_description_inline = False
            #  - show_counter = True
            soup = BeautifulSoup(html)
            links = soup.findAll('a')
            self.assert_(len(links) == 3)
            # check order
            order = [int(x)-1 for x in self.picset.order.split(",")]
            for idx, link in zip(order, links):
                self.assert_(link['href'] == self.pics[idx].url)
            self.assert_(html.find('inline_description') == -1)
            counter = soup.findAll('p', attrs={'class':'inline_counter'})
            self.assert_(len(counter) == 1)

    def test_full_with_reversed_default_options(self):
        tmpl = 'inline_media/inline_media.pictureset.full.html'
        positions = ['inline_full_left', 
                     'inline_full_center',
                     'inline_full_right']
        self._reverse_default_boolean_field_values()
        for cssclass in positions:
            html = inlines(self.tag % cssclass, return_list=False)
            self.assertTemplateUsed(html, tmpl)
            # default options:
            #  - show_description_inline = False
            #  - show_counter = True
            soup = BeautifulSoup(html)
            links = soup.findAll('a')
            self.assert_(len(links) == 3)
            # check order
            order = [int(x)-1 for x in self.picset.order.split(",")]
            for idx, link in zip(order, links):
                self.assert_(link['href'] == self.pics[idx].url)
            self.assert_(html.find('inline_description') == -1)
            counter = soup.findAll('p', attrs={'class':'inline_counter'})
            self.assert_(len(counter) == 1)
