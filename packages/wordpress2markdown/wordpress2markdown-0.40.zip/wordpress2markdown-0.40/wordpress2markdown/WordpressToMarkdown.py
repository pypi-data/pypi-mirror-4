#!/usr/bin/env python
# Written by: DGC

# This is an attempt to get near to markdown syntax from wordpress.com 
# editing syntax. This will take command line input as a single string.

# python imports
import argparse
import sys
import re

# local imports

#==============================================================================
class WordpressToMarkdown(object):

    def convert(self, wordpress_html_text):
        """
        Pass in wordpress.com style html and this will convert it to markdown
        syntax.
        
        Implementation detail:
        
        This passes over the text several times, converting a different 
        construction on each pass.
        
        Passes
        1) <h[1,2,3,4,5,6]> tags -> #, ##, ###, ####, #####, ###### pairs
        2) <a href="url">title</a> -> [title](url)
        3) [sourcecode language="lang"] -> ```lang
        4) [/sourcecode] -> ```
        5) <!-- --> comments deleted
        
        Unimplemented features:
        
        o ordered/unordered lists
        o images
        
        """
        wordpress_html_text = self.convert_h_tags(wordpress_html_text)
        wordpress_html_text = self.convert_links(wordpress_html_text)
        wordpress_html_text = self.convert_sourcecode(wordpress_html_text)
        wordpress_html_text = self.remove_html_comments(wordpress_html_text)
        return wordpress_html_text

    def remove_html_comments(self, html_text):
        regex = "<!--[^>]*-->"
        match = re.search(regex, html_text)
        while(match):
            comment = html_text[match.start():match.end()]
            html_text = "".join(
                [
                    html_text[0:match.start()],
                    html_text[match.end():],
                    ]
                )
            match = re.search(regex, html_text)
        return html_text

    def convert_links(self, html_text):
        regex = "<a [^>]*>[^<]*</a>"
        match = re.search(regex, html_text)
        while(match):
            element = html_text[match.start():match.end()]
            assert "href=\"" in element, "No link in <a> element"
            url = re.search("href=\"[^\"]*\"", element)
            # add 6 for the href=" -1 for the end "
            url = element[url.start() + 6:url.end() - 1]
            
            title = re.search(">.*<", element)
            title = element[title.start() + 1: title.end() - 1]

            html_text = "".join(
                [
                    html_text[0:match.start()],
                    "[",
                    title,
                    "](",
                    url,
                    ")",
                    html_text[match.end():],
                    ]
                )
            match = re.search(regex, html_text)
        return html_text

    def convert_h_tags(self, html_text):
        """
        Converts <h[1,2,3,4,5,6]> tags to #, ##, ###, ####, #####, ###### pairs
        """
        for i in range(1, 7):
            # replace opening and closing tags at once
            html_text = re.sub(
                "</?h" + str(i) + ">", 
                "#" * i, # convert the part to make h1 -> # or h2 -> ## etc.
                html_text
                )
        return html_text

    def convert_sourcecode(self, html_text):
        """
        Converts [sourcecode language="lang"...] into ```lang
        and [/sourcecode] into ```
        """
        regex = "\[sourcecode.*\]"
        match = re.search(regex, html_text)
        while (match):
            source_code = html_text[match.start():match.end()]
            language = ""
            if ("language" in source_code):
                language = re.search("language=\"[^\"]*\"", source_code)
                # +10 for language,=" -1 for trailing "
                language = source_code[language.start()+10:language.end()-1]
            html_text = "".join(
                [
                    html_text[0:match.start()],
                    "```",
                    language,
                    html_text[match.end():],
                    ]
                )
            match = re.search(regex, html_text)
        html_text = html_text.replace("[/sourcecode]", "```")
        return html_text

#==============================================================================
def main():
    """
    Get argument, then pass it to WordpressToMarkdown
    """
    des = "This script converts wordpress.com html into markdown syntax."
    parser = argparse.ArgumentParser(description=des)
    parser.add_argument("wordpress_html")
    parser.add_argument(
        "-f",
        "--file",
        help="Read the Wordpress.com html from a file",
        action="store_true"
        )

    args = parser.parse_args()
    converter = WordpressToMarkdown()
    source = args.wordpress_html
    if (args.file):
        with open(source, "r") as source_file:
            source = source_file.read()
    print(converter.convert(source))

#==============================================================================
if (__name__ == "__main__"):
    main()
