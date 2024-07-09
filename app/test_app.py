import unittest
from app import app, db, User
from flask import json
from datetime import datetime, timedelta, date

class TestHelloWorldApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.client = app.test_client()
        with app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        with app.app_context():
            db.drop_all()

    def setUp(self):
        with app.app_context():
            db.session.query(User).delete()
            db.session.commit()

    def test_save_user_invalid_username(self):
        response = self.client.put('/hello/invalid-username',
                                   data=json.dumps({"dateOfBirth": "1990-06-15"}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.decode(), "Invalid username")

    def test_save_user_invalid_date(self):
        response = self.client.put('/hello/johndoe',
                                   data=json.dumps({"dateOfBirth": "invalid-date"}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.decode(), "Invalid date format")

    def test_save_user_future_date(self):
        future_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.put('/hello/johndoe',
                                   data=json.dumps({"dateOfBirth": future_date}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.decode(), "dateOfBirth must be before today")

    def test_save_user(self):
        response = self.client.put('/hello/johndoe',
                                   data=json.dumps({"dateOfBirth": "1990-06-15"}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 204)

    def test_get_user_not_found(self):
        response = self.client.get('/hello/johndoe')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data.decode(), "User not found")

    def test_get_user_birthday_today(self):
        today_date = datetime.now().strftime('%Y-%m-%d')
        response = self.client.put('/hello/johndoe',
                        data=json.dumps({"dateOfBirth": today_date}),
                        content_type='application/json')
        self.assertEqual(response.status_code, 204)

        response = self.client.get('/hello/johndoe')
        self.assertEqual(response.status_code, 200)
        expected_message = {"message": f"Hello, johndoe! Happy birthday!"}
        self.assertEqual(response.json, expected_message)

    def test_get_user_birthday_today_5_years(self):
        today_date_5y_age = datetime.now().replace(year=2019).strftime('%Y-%m-%d')
        response = self.client.put('/hello/johndoe',
                        data=json.dumps({"dateOfBirth": today_date_5y_age}),
                        content_type='application/json')
        self.assertEqual(response.status_code, 204)

        response = self.client.get('/hello/johndoe')
        self.assertEqual(response.status_code, 200)
        expected_message = {"message": f"Hello, johndoe! Happy birthday!"}
        self.assertEqual(response.json, expected_message)

    def test_get_user_birthday_in_future(self):
        future_birthday = (datetime.now() - timedelta(days=359)).strftime('%Y-%m-%d')
        self.client.put('/hello/johndoe',
                        data=json.dumps({"dateOfBirth": future_birthday}),
                        content_type='application/json')

        response = self.client.get('/hello/johndoe')
        self.assertEqual(response.status_code, 200)
        expected_message = {"message": f"Hello, johndoe! Your birthday is in 7 day(s)"}
        self.assertEqual(response.json, expected_message)

if __name__ == '__main__':
    unittest.main()
