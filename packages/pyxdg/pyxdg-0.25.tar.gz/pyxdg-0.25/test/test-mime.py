from xdg import Mime
import unittest
import os.path
import tempfile, shutil

import resources

class MimeTest(unittest.TestCase):
    def check_mimetype(self, mimetype, media, subtype):
        self.assertEqual(mimetype.media, media)
        self.assertEqual(mimetype.subtype, subtype)
    
    def test_get_type_by_name(self):
        appzip = Mime.get_type_by_name("foo.zip")
        self.check_mimetype(appzip, 'application', 'zip')
    
    def test_get_type_by_data(self):
        imgpng = Mime.get_type_by_data(resources.png_data)
        self.check_mimetype(imgpng, 'image', 'png')
    
    def test_get_type_by_contents(self):
        tmpdir = tempfile.mkdtemp()
        try:
            test_file = os.path.join(tmpdir, "test")
            with open(test_file, "wb") as f:
                f.write(resources.png_data)
            
            imgpng = Mime.get_type_by_contents(test_file)
            self.check_mimetype(imgpng, 'image', 'png')
        
        finally:
            shutil.rmtree(tmpdir)
    
    def test_get_type(self):
        tmpdir = tempfile.mkdtemp()
        try:
            # File that doesn't exist - get type by name
            path = os.path.join(tmpdir, "test.png")
            imgpng = Mime.get_type(path)
            self.check_mimetype(imgpng, 'image', 'png')
            
            # File that does exist - get type by contents
            path = os.path.join(tmpdir, "test")
            with open(path, "wb") as f:
                f.write(resources.png_data)
            imgpng = Mime.get_type(path)
            self.check_mimetype(imgpng, 'image', 'png')
        
            # Directory - special case
            path = os.path.join(tmpdir, "test2")
            os.mkdir(path)
            inodedir = Mime.get_type(path)
            self.check_mimetype(inodedir, 'inode', 'directory')
        
        finally:
            shutil.rmtree(tmpdir)
    
    def test_lookup(self):
        pdf1 = Mime.lookup("application/pdf")
        pdf2 = Mime.lookup("application", "pdf")
        self.assertEqual(pdf1, pdf2)
        self.check_mimetype(pdf1, 'application', 'pdf')
        
        pdf1.get_comment()

    def test_by_name(self):
        dot_c = Mime.get_type_by_name('foo.c')
        self.check_mimetype(dot_c, 'text', 'x-csrc')
        dot_C = Mime.get_type_by_name('foo.C')
        self.check_mimetype(dot_C, 'text', 'x-c++src')
    
    def test_canonical(self):
        text_xml = Mime.lookup('text/xml')
        self.check_mimetype(text_xml, 'text', 'xml')
        self.check_mimetype(text_xml.canonical(), 'application', 'xml')
    
    def test_inheritance(self):
        text_python = Mime.lookup('text/x-python')
        self.check_mimetype(text_python, 'text', 'x-python')
        text_plain = Mime.lookup('text/plain')
        app_executable = Mime.lookup('application/x-executable')
        self.assertEqual(text_python.inherits_from(), set([text_plain, app_executable]))
