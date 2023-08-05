from Products.BlingPortlet.interfaces import IBlingImage
from Products.BlingPortlet.tests.base import TestCase

from Products.ATContentTypes.tests.test_atimage import loadImage
icon = loadImage('test.gif')

class TestAdapter(TestCase):

    def testATImageAdapter(self):
        self.setRoles(('Manager',))
        
        title= u"Test Image 1"
        description= u"This is a test image."
        
        self.portal.invokeFactory('Image', 'image-1', title=title, description=description)
        img = self.portal['image-1']
        itemurl = img.absolute_url()
        blimg = IBlingImage(img)
        
        self.assertEquals(blimg.getTitle(), 'Test Image 1')
        self.assertEquals(blimg.getDescription(), 'This is a test image.')
        self.assertEquals(blimg.getLink(),  '%s/view' % itemurl)
        self.assertEquals(blimg.getImage(), itemurl)
        self.assertEquals(blimg.getImage('normal'), '%s/image_normal' % itemurl)


    def testATNewsItemAdapter(self):
        self.setRoles(('Manager',))
        
        title = u"Test News Item 1"
        description = u"This is a test news item."

        self.portal.invokeFactory('News Item', 'news-1', title=title, description=description)
        news = self.portal['news-1']
        itemurl = news.absolute_url()
        blimg = IBlingImage(news)

        self.assertEquals(blimg.getTitle(), title)
        self.assertEquals(blimg.getDescription(), description)
        self.assertEquals(blimg.getLink(),  '%s' % itemurl)
        self.assertEquals(blimg.getImage(), '') # since we have no image, we expect an empty URL

        title = u"Test News Item 2"
        description = u"This is a test news item."

        self.portal.invokeFactory('News Item', 'news-2', title=title, description=description)
        news = self.portal['news-2']
        news.setImage(icon)
        itemurl = news.absolute_url()
        blimg = IBlingImage(news)

        self.assertEquals(blimg.getTitle(), title)
        self.assertEquals(blimg.getDescription(), description)
        self.assertEquals(blimg.getLink(),  '%s' % itemurl)
        self.assertEquals(blimg.getImage(), 'http://nohost/plone/news-2/image')
        self.assertEquals(blimg.getImage('normal'), 'http://nohost/plone/news-2/image_normal')
        

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAdapter))
    return suite
        