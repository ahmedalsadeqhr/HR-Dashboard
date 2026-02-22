"""Smoke tests: every page module imports and has a render callable."""


def test_overview_importable():
    from src.pages import overview
    assert callable(overview.render)


def test_attrition_importable():
    from src.pages import attrition
    assert callable(attrition.render)


def test_tenure_retention_importable():
    from src.pages import tenure_retention
    assert callable(tenure_retention.render)


def test_workforce_importable():
    from src.pages import workforce
    assert callable(workforce.render)


def test_trends_importable():
    from src.pages import trends
    assert callable(trends.render)


def test_employee_data_importable():
    from src.pages import employee_data
    assert callable(employee_data.render)


def test_advanced_analytics_importable():
    from src.pages import advanced_analytics
    assert callable(advanced_analytics.render)


def test_edit_data_importable():
    from src.pages import edit_data
    assert callable(edit_data.render)
