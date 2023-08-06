from pytest import fixture


@fixture
def contentpreview_populate_settings(db_session):
    from kotti_contentpreview.populate import populate
    populate()
