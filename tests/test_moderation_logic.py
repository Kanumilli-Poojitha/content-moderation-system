def moderate_text(text: str) -> str:
    if "badword" in text.lower():
        return "REJECTED"
    return "APPROVED"

def test_badword_rejected():
    result = moderate_text("this has badword in it")
    assert result == "REJECTED"

def test_clean_text_approved():
    result = moderate_text("this is clean content")
    assert result == "APPROVED"