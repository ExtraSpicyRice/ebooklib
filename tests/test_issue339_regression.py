import pytest
from ebooklib import epub, utils


def make_chapter(markup):
    chapter = epub.EpubHtml(
        uid="chapter",
        file_name="chapter.xhtml",
        title="Chapter"
    )
    chapter.set_content(markup)
    return chapter


def test_unrelated_epub_types_are_ignored():
    chapter = make_chapter(
        '<section id="copyright" epub:type="copyright-page">'
        'Copyright</section>'
        '<aside id="note" epub:type="footnote">'
        'Example note</aside>'
    )

    assert utils.get_pages(chapter) == []


def test_only_real_pagebreaks_are_included():
    chapter = make_chapter(
        '<section id="copyright" epub:type="copyright-page">'
        'Copyright</section>'
        '<span id="p1" epub:type="pagebreak">1</span>'
        '<span id="p2" epub:type="chapter pagebreak" '
        'aria-label="Page two"></span>'
        '<span id="p3" epub:type="chapter\tpagebreak\nfootnote">'
        '3</span>'
        '<span id="not-page" epub:type="pagebreak-extra">'
        'Not a page</span>'
    )

    assert utils.get_pages(chapter) == [
        ("chapter.xhtml", "p1", "1"),
        ("chapter.xhtml", "p2", "Page two"),
        ("chapter.xhtml", "p3", "3"),
    ]


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        (
            '<span id="p" epub:type="pagebreak">4</span>',
            [("chapter.xhtml", "p", "4")]
        ),
        (
            '<span id="p" epub:type="chapter pagebreak" '
            'aria-label="Four"></span>',
            [("chapter.xhtml", "p", "Four")]
        ),
        (
            '<span id="p" epub:type="pagebreak-extra">4</span>',
            []
        ),
        (
            '<span id="p" epub:type="pagebreaks">4</span>',
            []
        ),
    ]
)
def test_exact_pagebreak_matching(markup, expected):
    chapter = make_chapter(markup)
    assert utils.get_pages(chapter) == expected
