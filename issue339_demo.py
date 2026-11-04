import io
import zipfile

from lxml import etree

from ebooklib import epub, utils


chapter = epub.EpubHtml(
    uid="chapter",
    file_name="chapter.xhtml",
    title="Example"
)

chapter.set_content(
    '<section id="copyright" epub:type="copyright-page">'
    'Copyright</section>'
    '<span id="page-1" epub:type="pagebreak">1</span>'
    '<aside id="note" epub:type="footnote">'
    'Extra note</aside>'
    '<span id="page-2" epub:type="chapter pagebreak" '
    'aria-label="2"></span>'
    '<span id="false-positive" epub:type="pagebreak-extra">'
    'Not a page</span>'
)


expected = [
    ("chapter.xhtml", "page-1", "1"),
    ("chapter.xhtml", "page-2", "2")
]

actual = utils.get_pages(chapter)

print("Issue #339 - EPUB page list")
print("Expected:", expected)
print("Actual:  ", actual)

print(
    "RESULT:  ",
    "PASS" if actual == expected else "FAIL"
)


book = epub.EpubBook()
book.set_identifier("issue-339-demo")
book.set_title("Page list demonstration")
book.set_language("en")

book.add_item(chapter)
book.add_item(epub.EpubNav())

book.toc = (chapter,)
book.spine = ["nav", chapter]

output = io.BytesIO()
epub.write_epub(output, book)
output.seek(0)

with zipfile.ZipFile(output) as archive:
    nav = etree.fromstring(
        archive.read("EPUB/nav.xhtml")
    )

    ns = epub.NAMESPACES

    xpath = (
        f'.//{{{ns["XHTML"]}}}nav'
        f'[@{{{ns["EPUB"]}}}type="page-list"]'
        f'//{{{ns["XHTML"]}}}a'
    )

    links = [
        (node.get("href"), node.text)
        for node in nav.findall(xpath)
    ]


expected_links = [
    ("chapter.xhtml#page-1", "1"),
    ("chapter.xhtml#page-2", "2")
]

print("Generated EPUB navigation links:", links)

print(
    "EPUB navigation check:",
    "PASS" if links == expected_links else "FAIL"
)

if actual != expected or links != expected_links:
    raise SystemExit(1)