import json

from pipeline.graph.nodes import parse_json_result


def test_parse_json_result_strict():
    data = {"foo": "bar"}
    assert parse_json_result(json.dumps(data)) == data

def test_parse_json_result_markdown():
    data = {"foo": "bar"}
    markdown = f"Here is the result:\n```json\n{json.dumps(data)}\n```"
    assert parse_json_result(markdown) == data

def test_parse_json_result_preamble():
    data = [{"id": 1}]
    text = f"Sure, here is your list: {json.dumps(data)}. Hope it helps!"
    assert parse_json_result(text) == data

def test_parse_json_result_invalid():
    assert parse_json_result("not a json") is None
