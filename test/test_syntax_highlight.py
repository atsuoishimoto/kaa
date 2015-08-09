import kaa_testutils
from kaa import syntax_highlight

class TestHighlight(kaa_testutils._TestDocBase):
    def test_token(self):
        doc = self._getdoc(' abc def ghi ')

        root = syntax_highlight.Root([
            ('keyword', syntax_highlight.Keywords('keyword', ['abc', 'ghi']))
        ])

        tokenizer = syntax_highlight.begin_tokenizer(
            doc, root, 0, doc.endpos(), 0)

        styles = list(tokenizer)
        assert styles == [
            (0, 1, root.styleid_default), 
            (1, 4, root.tokens.keyword.styleid_token), 
            (4, 9, root.styleid_default), 
            (9, 12, root.tokens.keyword.styleid_token),
            (12, 13, root.styleid_default),]

    def test_span(self):
        doc = self._getdoc(' ab\\cc def ghi ')

        root = syntax_highlight.Root([
            ('span1', syntax_highlight.Span('span', 'a', 'c',
                escape='\\')),
            ('span2', syntax_highlight.Span('span', 'd', 'f', 
                capture_end=False)),
            ('span3', syntax_highlight.Span('span', 'g', 'i', terminates='h')),
        ])

        tokenizer = syntax_highlight.begin_tokenizer(
            doc, root, 0, doc.endpos(), 0)

        styles = list(tokenizer)
        assert styles == [
            (0, 1, root.styleid_default), 
            (1, 2, root.tokens.span1.styleid_begin), 
            (2, 5, root.tokens.span1.styleid_mid), 
            (5, 6, root.tokens.span1.styleid_end), 
            (6, 7, root.styleid_default), 
            (7, 8, root.tokens.span2.styleid_begin), 
            (8, 9, root.tokens.span2.styleid_mid), 
            (9, 11, root.styleid_default), 
            (11, 12, root.tokens.span3.styleid_begin), 
            (12, 15, root.styleid_default), 
        ]

    def test_resume(self):
        doc = self._getdoc('    abc')

        root = syntax_highlight.Root(
            [('keyword', syntax_highlight.Keywords('keyword', ['abc', 'ghi']))])

        tokeniter = syntax_highlight.begin_tokenizer(
            doc, root, 0, doc.endpos(), 2)

        styles = list(tokeniter)
        assert styles == [
            (0, 4, root.styleid_default), 
            (4, 7, root.tokens.keyword.styleid_token)]

        tokeniter = syntax_highlight.begin_tokenizer(
            doc, root, 0, doc.endpos(), 6)

        doc.styles.setints(4, 7, root.tokens.keyword.styleid_token)
        styles = list(tokeniter)
        assert styles == [
            (4, 7, root.tokens.keyword.styleid_token)]


class TestHighlight_Nest(kaa_testutils._TestDocBase):
    def test_nest_resume(self):

        doc = self._getdoc('   abc   123')

        class SubKeyword(syntax_highlight.Keywords):
            def on_start(self, doc, match, end):
                pos = yield from super().on_start(doc, match, end)
                return (yield from sub.run(doc, pos, end))

        root = syntax_highlight.Root([
            ('subkeyword', SubKeyword('keyword', ['abc']))])

        sub = syntax_highlight.Tokenizer(root, None, 
            [('keyword', syntax_highlight.Keywords('keyword', ['123']))])


        doc.styles.setints(0, 3, root.styleid_default)
        doc.styles.setints(3, 6, root.tokens.subkeyword.styleid_token)
        doc.styles.setints(6, 9, sub.styleid_default)
        doc.styles.setints(9, 12, sub.tokens.keyword.styleid_token)

        # parse at blank
        tokeniter = syntax_highlight.begin_tokenizer(
            doc, root, 0, doc.endpos(), 2)

        styles = list(tokeniter)
        assert styles == [
            (0, 3, root.styleid_default),
            (3, 6, root.tokens.subkeyword.styleid_token),
            (6, 9, sub.styleid_default),
            (9, 12, sub.tokens.keyword.styleid_token)]


        # parse at first token
        tokeniter = syntax_highlight.begin_tokenizer(
            doc, root, 0, doc.endpos(), 4)

        styles = list(tokeniter)
        assert styles == [
            (3, 6, root.tokens.subkeyword.styleid_token),
            (6, 9, sub.styleid_default),
            (9, 12, sub.tokens.keyword.styleid_token)]

        # parse at blank of sub2
        tokeniter = syntax_highlight.begin_tokenizer(
            doc, root, 0, doc.endpos(), 8)

        styles = list(tokeniter)
        assert styles == [
            (6, 9, sub.styleid_default),
            (9, 12, sub.tokens.keyword.styleid_token)]


        # parse at blank of keyword2
        tokeniter = syntax_highlight.begin_tokenizer(
            doc, root, 0, doc.endpos(), 11)

        styles = list(tokeniter)
        assert styles == [
            (9, 12, sub.tokens.keyword.styleid_token)]

