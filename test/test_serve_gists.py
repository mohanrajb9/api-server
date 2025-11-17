""" Unit tests for gets public gists of an user."""

import unittest
import time
import os
import subprocess
from http import HTTPStatus
import requests


HOST = "http://127.0.0.1"
PORT = 8080
IMAGE_NAME = "gist-app"
CONTAINER_NAME = "gist-app-container"
TEST_PATH = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.abspath(os.path.join(TEST_PATH, ".."))
ROOT_URL = f"{HOST}:{PORT}"


class TestServeGistsCoverage(unittest.TestCase):
    """ Setup, tests and teardown of the server"""

    @classmethod
    def setUpClass(cls):
        """Build Docker image and start container before tests."""
        # Check if image exists
        result = subprocess.run(
            ["docker", "images", "-q", IMAGE_NAME],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        if result.stdout.strip():
            print(f"Docker image '{IMAGE_NAME}' exists. Skipping build.")
        else:
            print(f"Building Docker image '{IMAGE_NAME}'...")
            subprocess.run(
                ["docker", "build", "-t", IMAGE_NAME, SRC_PATH],
                check=True
            )

        # Start container
        print(f"Starting Docker container '{CONTAINER_NAME}'...")
        subprocess.run([
            "docker", "run", "--rm", "-d",
            "-p", f"{PORT}:{PORT}",
            "--name", CONTAINER_NAME,
            IMAGE_NAME
        ], check=True)

        print("Waiting for server to be ready...")
        time.sleep(10)

    @classmethod
    def tearDownClass(cls):
        """
        Shut down the server after tests.
        """
        print("Stopping Docker container...")
        subprocess.run(["docker", "stop", f"{CONTAINER_NAME}"], check=False)
        print(f"Removing Docker image '{IMAGE_NAME}'...")
        subprocess.run([
            "docker", "rmi", "-f", IMAGE_NAME],
            stderr=subprocess.DEVNULL, check=False
        )

    def test_valid_user_with_response(self):
        """ valid user with public gists"""
        response = requests.get(f"{HOST}:{PORT}/octocat", timeout=10)
        public_gists = response.json()
        self.assertIn("gists_list", public_gists)
        self.assertGreater(len(public_gists["gists_list"]), 0)

    def test_valid_user_no_response(self):
        """ Test valid user with no public gists"""
        response = requests.get(f"{ROOT_URL}/ionico", timeout=10)
        public_gists = response.json()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(public_gists["gists_list"], [])

    def test_invalid_user(self):
        """ Test invalid user"""
        response = requests.get(f"{ROOT_URL}/invalid-user-invalid", timeout=10)
        public_gists = response.json()
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertIn("User not found", public_gists['error'])

    def test_empty_path(self):
        """ Test empty path to get usage message"""
        response = requests.get(f"{ROOT_URL}/", timeout=10)
        public_gists = response.json()
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIn("Usage - 127.0.0.1", public_gists['error'])

    def test_favicon(self):
        """ Test favicon request"""
        response = requests.get(f"{ROOT_URL}/favicon.ico", timeout=10)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.text, "")

    def test_invalid_format(self):
        """ Test invalid path format"""
        response = requests.get(f"{ROOT_URL}/user/name", timeout=10)
        public_gists = response.json()
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIn("Usage - 127.0.0.1", public_gists['error'])

    def test_invalid_query_param(self):
        """ Test invalid query format"""
        response = requests.get(f"{ROOT_URL}/user?query", timeout=10)
        public_gists = response.json()
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIn("Usage - 127.0.0.1", public_gists['error'])

    def test_invalid_query_value_param(self):
        """ Test invalid query format"""
        response = requests.get(f"{ROOT_URL}/user?page=as", timeout=10)
        public_gists = response.json()
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIn("Usage - 127.0.0.1", public_gists['error'])


if __name__ == "__main__":
    unittest.main()
