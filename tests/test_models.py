from app.models import User, Folder, Bookmark, db

def test_create_user(test_app):
    user = User(username="alice")
    db.session.add(user)
    db.session.commit()

    assert User.query.filter_by(username="alice").first() is not None


def test_create_folder(test_app):
    user = User.query.filter_by(username="testuser").first()

    folder = Folder(name="Homework", user_id=user.id)
    db.session.add(folder)
    db.session.commit()

    assert Folder.query.filter_by(name="Homework").first() is not None


def test_create_bookmark_with_folder(test_app):
    user = User.query.filter_by(username="testuser").first()

    folder = Folder(name="Lectures", user_id=user.id)
    db.session.add(folder)
    db.session.commit()

    bm = Bookmark(title="Week 1 Slides", url="https://example.com", user_id=user.id, folder_id=folder.id)
    db.session.add(bm)
    db.session.commit()

    assert Bookmark.query.filter_by(title="Week 1 Slides").first().folder_id == folder.id
