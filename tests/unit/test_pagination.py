from shopcart.domain.pagination import PageRequest


def test_defaults():
    page = PageRequest()
    assert page.page == 1
    assert page.limit == 10


def test_page_count_rounds_up():
    assert PageRequest(size=10).pages_for(21) == 3


def test_at_least_one_page_when_empty():
    assert PageRequest(size=10).pages_for(0) == 1
