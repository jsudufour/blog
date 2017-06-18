import os
import unittest
import multiprocessing
import time
from urllib.parse import urlparse

from werkzeug.security import generate_password_hash
from splinter import Browser

# Configure your app to use the testing database
os.environ["CONFIG_PATH"] = "blog.config.TestingConfig"

from blog import app
from blog.database import Base, engine, session, User, Entry

class TestViews(unittest.TestCase):
    def setUp(self):
        """ Test setup """
        # self.browser = Browser('chrome')
        self.browser = Browser("phantomjs")

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create an example user
        self.user = User(name="Mary", email="mary@example.com",
                         password=generate_password_hash("test"))
        session.add(self.user)
        session.commit()

        self.process = multiprocessing.Process(target=app.run,
                                               kwargs={"port": 8080})
        self.process.start()
        time.sleep(1)

    def test_login_correct(self):
        self.browser.visit("http://127.0.0.1:8080/login")
        self.browser.fill("email", "mary@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("#login-submit")
        button.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/")

    def test_login_incorrect(self):
        self.browser.visit("http://127.0.0.1:8080/login")
        self.browser.fill("email", "bob@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("#login-submit")
        button.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/login")

    def test_entry_add(self):
        self.browser.visit("http://127.0.0.1:8080/login")
        self.browser.fill("email", "mary@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("#login-submit")
        button.click()
        self.browser.visit("http://127.0.0.1:8080/entry/add")
        self.browser.fill_form({"title": "TestTitle"})
        self.browser.fill_form({"content": "TestContent"})
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/")

    def test_edit_entry(self):
        session.add(Entry(title="test",content="Testing"))
        session.commit()
        self.browser.visit("http://127.0.0.1:8080/login")
        self.browser.fill("email", "mary@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("#login-submit")
        button.click()
        link = self.browser.find_link_by_partial_href("/edit")[0]
        link.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/entry/0/edit")

    def test_delete_entry_cancel(self):
        session.add(Entry(title="test",content="Testing"))
        session.commit()
        self.browser.visit("http://127.0.0.1:8080/login")
        self.browser.fill("email", "mary@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("#login-submit")
        button.click()
        link = self.browser.find_link_by_partial_href("/confirm-delete")[0]
        link.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/entry/0/confirm-delete")
        link = self.browser.find_link_by_partial_href("/")[0]
        link.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/")

    def test_delete_entry_delete(self):
        session.add(Entry(title="test",content="Testing"))
        session.commit()
        self.browser.visit("http://127.0.0.1:8080/login")
        self.browser.fill("email", "mary@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("#login-submit")
        button.click()
        link = self.browser.find_link_by_partial_href("/confirm-delete")[0]
        link.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/entry/0/confirm-delete")
        link = self.browser.find_link_by_partial_href("/delete")[0]
        link.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/")

    def test_view_single_entry(self):
        session.add(Entry(title="test",content="Testing"))
        session.commit()
        self.browser.visit("http://127.0.0.1:8080/login")
        self.browser.fill("email", "mary@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("#login-submit")
        button.click()
        link = self.browser.find_link_by_href("/entry/0")[0]
        link.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/entry/0")

    def tearDown(self):
        """ Test teardown """
        # Remove the tables and their data from the database
        self.process.terminate()
        session.close()
        engine.dispose()
        Base.metadata.drop_all(engine)
        # self.browser.quit()

if __name__ == "__main__":
    unittest.main()
