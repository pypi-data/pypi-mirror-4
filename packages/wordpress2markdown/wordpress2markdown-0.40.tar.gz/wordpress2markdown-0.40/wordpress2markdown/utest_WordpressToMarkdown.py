#!/usr/bin/env python
# Written by: DGC

# python imports
import unittest

# local imports
from WordpressToMarkdown import WordpressToMarkdown

#==============================================================================
class utest_WordpressToMarkdown(unittest.TestCase):
    
    def test_normal_text(self):
        converter = WordpressToMarkdown()
        text = """\
Hi, this is a normal sentence. With no html rubbish.
"""
        result = converter.convert(text)
        self.assertEqual(text, result)

    def test_header(self):
        text_with_h1 = """\
<h1>This is a header</h1>
"""
        expected_result = """\
#This is a header#
"""
        converter = WordpressToMarkdown()
        result = converter.convert(text_with_h1)
        self.assertEqual(
            result,
            expected_result
            )

        text_with_all_h_tags = """\
<h1>H1</h1>
<h2>H2</h2>
<h3>H3</h3>
<h4>H4</h4>
<h5>H5</h5>
<h6>H6</h6>
"""
        expected_result = """\
#H1#
##H2##
###H3###
####H4####
#####H5#####
######H6######
"""
        converter = WordpressToMarkdown()
        result = converter.convert(text_with_all_h_tags)
        self.assertEqual(
            result,
            expected_result
            )

    def test_links(self):
        test_link = """\
<a href="www.example.com">link</a>
"""
        expected_result = """\
[link](www.example.com)
"""
        converter = WordpressToMarkdown()
        result = converter.convert(test_link)
        self.assertEqual(
            result,
            expected_result
            )
        test_link_new_page = """\
<a href="www.example.com" target="_blank">link</a>
"""
        expected_result = """\
[link](www.example.com)
"""
        result = converter.convert(test_link_new_page)
        self.assertEqual(
            result,
            expected_result
            )

    def test_source_code(self):
        test_source="""
[sourcecode]
"""
        expected_result="""
```
"""
        converter = WordpressToMarkdown()
        result = converter.convert(test_source)
        self.assertEqual(expected_result, result)

        test_source="""
[sourcecode]
Some code.
[/sourcecode]
"""
        expected_result="""
```
Some code.
```
"""
        result = converter.convert(test_source)
        self.assertEqual(expected_result, result)

        language_source="""
[sourcecode language="python" firstline="8"]
python code
[/sourcecode]
"""
        expected_result="""
```python
python code
```
"""
        result = converter.convert(language_source)
        self.assertEqual(expected_result, result)
        

    def test_example(self):
        """ 
        This is an example of a bug so that it will stay fixed.
        """
        test_paragraph = """
[/sourcecode]

This is however wrong! As python does not use deterministic garbage collection __del__ will not necessarily ever get called. <a href="http://docs.python.org/2/reference/datamodel.html#object.__del__" target="_blank">Here</a> there is more information about when/how/if __del__ is called. As a side not python is even not guaranteed to be garbage collected, this is an implementation detail for each specific interpreter, see <a href="http://docs.python.org/2/reference/datamodel.html" target="_blank">here</a>.

"""
        expected_result = """
```

This is however wrong! As python does not use deterministic garbage collection __del__ will not necessarily ever get called. [Here](http://docs.python.org/2/reference/datamodel.html#object.__del__) there is more information about when/how/if __del__ is called. As a side not python is even not guaranteed to be garbage collected, this is an implementation detail for each specific interpreter, see [here](http://docs.python.org/2/reference/datamodel.html).

"""
        converter = WordpressToMarkdown()
        result = converter.convert(test_paragraph)
        # print a message here as the diff is not readable.
        self.assertEqual(
            expected_result,
            result,
            "Test paragraph not as expected."
            )

    def test_more(self):
        """
        Test it removes the <!--more--> flag (and any html comments in fact.)
        """
        comment="""
<!--more-->
"""
        expected_result="""

"""
        converter = WordpressToMarkdown()
        result = converter.convert(comment)
        self.assertEqual(expected_result, result)

#==============================================================================
if (__name__ == "__main__"):
    unittest.main(verbosity=2)
