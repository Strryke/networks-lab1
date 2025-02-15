import requests
import os

BASE_URL = os.getenv("BASE_URL", "http://app:8000")


def test_get_books():
    """Get all books"""
    response = requests.get(f"{BASE_URL}/books")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_sorted_books():
    """Get all books sorted by title"""
    response = requests.get(f"{BASE_URL}/books?sort=title")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["title"] < response.json()[1]["title"]


def test_get_limited_books():
    """Limit the number of books returned"""
    response = requests.get(f"{BASE_URL}/books?count=1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1

    response = requests.get(f"{BASE_URL}/books?count=2")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2


def test_get_sorted_and_limited_books():
    """Allow both"""
    response = requests.get(f"{BASE_URL}/books?sort=title&count=3")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 3
    assert response.json()[0]["title"] < response.json()[1]["title"]


def test_create_book():
    """Create a book and check that it is in the database"""
    new_book = {"title": "Test Book", "author": "Test Author"}
    response = requests.post(f"{BASE_URL}/books", json=new_book)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json()["message"] == "Book added"
    assert response.json()["book"]["title"] == "Test Book"
    assert response.json()["book"]["author"] == "Test Author"

    new_id = response.json()["book"]["id"]

    # show that the book is in the database
    response = requests.get(f"{BASE_URL}/books/{new_id}")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json()["title"] == "Test Book"
    assert response.json()["author"] == "Test Author"


def test_invalid_book_creation():
    """Test required fields"""
    new_book = {"title": "Test Book"}
    response = requests.post(f"{BASE_URL}/books", json=new_book)
    assert response.status_code == 422


def test_modify_book():
    """Create, test and modify a book"""
    # first we create a book
    new_book = {"title": "Test Book", "author": "Test Author"}
    response = requests.post(f"{BASE_URL}/books", json=new_book)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json()["message"] == "Book added"
    book_id = response.json()["book"]["id"]

    # then we modify the book
    modified_book = {"title": "Modified Book", "author": "Modified Author"}
    response = requests.put(f"{BASE_URL}/books/{book_id}", json=modified_book)
    assert response.status_code == 200

    # then we check that the book was modified
    response = requests.get(f"{BASE_URL}/books/{book_id}")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json()["title"] == "Modified Book"
    assert response.json()["author"] == "Modified Author"


def test_invalid_book_modification():
    """Test invalid book modification"""
    modified_book = {"title": "Modified Book", "author": "Modified Author"}
    response = requests.put(f"{BASE_URL}/books/123123123123", json=modified_book)
    assert response.status_code == 404

    extra_field_book = {
        "title": "Modified Book",
        "author": "Modified Author",
        "extra_field": "Extra Field",
    }
    response = requests.put(f"{BASE_URL}/books/1", json=extra_field_book)
    assert response.status_code == 422


def test_delete_book():
    """Delete a book"""
    # first we create a book
    new_book = {"title": "Test Book", "author": "Test Author"}
    response = requests.post(f"{BASE_URL}/books", json=new_book)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json()["message"] == "Book added"
    book_id = response.json()["book"]["id"]

    response = requests.delete(f"{BASE_URL}/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Book deleted"

    # try to get the book
    response = requests.get(f"{BASE_URL}/books/{book_id}")
    assert response.status_code == 404


def test_delete_non_existent_book():
    """Can't delete a non-existent book"""
    response = requests.delete(f"{BASE_URL}/books/123123123123")
    assert response.status_code == 404


def test_delete_batch_books():
    """Delete a batch of books"""
    books = [
        {"title": f"Test Book {i}", "author": f"Test Author {i}"} for i in range(5)
    ]
    book_ids = []

    for book in books:
        response = requests.post(f"{BASE_URL}/books", json=book)
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
        assert response.json()["message"] == "Book added"
        book_ids.append(response.json()["book"]["id"])

    response = requests.delete(f"{BASE_URL}/books/batch", params={"book_ids": book_ids})
    assert response.status_code == 200
    assert response.json()["message"] == f"{len(book_ids)} books deleted"

    for book_id in book_ids:
        response = requests.get(f"{BASE_URL}/books/{book_id}")
        assert response.status_code == 404


def test_admin_page():
    """Test the admin page with a valid password"""
    response = requests.get(
        f"{BASE_URL}/admin", headers={"Authorization": "admin:password"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Admin page"


def test_admin_page_unauthorized():
    """Test the admin page with an invalid password"""
    response = requests.get(
        f"{BASE_URL}/admin", headers={"Authorization": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"


def test_admin_page_no_authorization():
    """You need headers"""
    response = requests.get(f"{BASE_URL}/admin")
    assert response.status_code == 401
    assert response.json()["detail"] == "No Authorization header provided"
