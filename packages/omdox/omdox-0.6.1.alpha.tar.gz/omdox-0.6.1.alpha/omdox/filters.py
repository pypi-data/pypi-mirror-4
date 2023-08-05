import re
import pygments
from pygments import lexers, formatters
from bs4 import BeautifulSoup
import markdown2 as md


def markdown(content):
    return md.markdown(
        content,
        extras=[
            'footnotes',
            'markdown-in-html',
            'smarty-pants',
            'header-ids'], )


def pygmentize(content):
    code_regex = re.compile(r'(<code(.*?)</code>)', re.DOTALL)
    code_blocks = []
    for i, m in enumerate(code_regex.finditer(content)):
        code = m.group(0)
        # if there is a lang attribute, use that
        if code.find('lang') > 0:
            soup = BeautifulSoup(code)
            language = soup.code['lang'] 
            # TODO: catch errors here and provide a default lexer
            lexer = lexers.get_lexer_by_name(language)
            # remove the code tags
            code = code.replace('</code>', '')
            code = code.replace('<code>', '')
            code = re.sub('<code(.*?)>', '', code)
            # create the pygmented code with the lexer
            pygmented_string = pygments.highlight(
                    code,
                    lexer,
                    formatters.HtmlFormatter())
            # put the code blocks into the list for processintg later
            code_blocks.append(pygmented_string)
        else:
            # this is for the inline code snippets
            code_blocks.append(code)
        # replace <code> tags with placeholders 
        content = content.replace(
                m.string[m.start():m.end()], 'OMCB|%s|OMCB' % i)
    # now do the replace
    for i, code in enumerate(code_blocks):
        content = content.replace('<p>OMCB|%s|OMCB</p>' % i, code)
        content = content.replace('OMCB|%s|OMCB' % i, code)
    return content
