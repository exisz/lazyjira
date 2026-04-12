"""Tests for lazyjira.format module."""

from lazyjira.format import markdown_to_adf, adf_to_text


class TestMarkdownToAdf:
    def test_simple_paragraph(self):
        result = markdown_to_adf("Hello world")
        assert result["type"] == "doc"
        assert result["version"] == 1
        assert len(result["content"]) == 1
        assert result["content"][0]["type"] == "paragraph"

    def test_heading(self):
        result = markdown_to_adf("## My Heading")
        assert result["content"][0]["type"] == "heading"
        assert result["content"][0]["attrs"]["level"] == 2

    def test_bullet_list(self):
        result = markdown_to_adf("- item 1\n- item 2")
        assert result["content"][0]["type"] == "bulletList"
        assert len(result["content"][0]["content"]) == 2

    def test_code_block(self):
        result = markdown_to_adf("```python\nprint('hi')\n```")
        assert result["content"][0]["type"] == "codeBlock"
        assert result["content"][0]["attrs"]["language"] == "python"

    def test_bold_inline(self):
        result = markdown_to_adf("this is **bold** text")
        para = result["content"][0]
        marks = [n.get("marks", []) for n in para["content"]]
        strong_found = any(
            any(m["type"] == "strong" for m in mark_list)
            for mark_list in marks
        )
        assert strong_found

    def test_table(self):
        md = "| A | B |\n| --- | --- |\n| 1 | 2 |"
        result = markdown_to_adf(md)
        assert result["content"][0]["type"] == "table"


class TestAdfToText:
    def test_simple_paragraph(self):
        adf = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Hello"}],
                }
            ],
        }
        assert "Hello" in adf_to_text(adf)

    def test_bullet_list(self):
        adf = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "item"}],
                                }
                            ],
                        }
                    ],
                }
            ],
        }
        result = adf_to_text(adf)
        assert "item" in result

    def test_non_dict_input(self):
        assert adf_to_text("plain string") == "plain string"
