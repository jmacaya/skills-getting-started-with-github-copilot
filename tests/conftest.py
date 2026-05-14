import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def mock_activities():
    """Fixture providing clean mock activity data for testing."""
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["alice@mergington.edu", "bob@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["charlie@mergington.edu"]
        },
        "Art Workshop": {
            "description": "Explore drawing, painting, and mixed media techniques",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": []
        }
    }


@pytest.fixture
def client(mock_activities):
    """Fixture providing a test client with isolated activity data."""
    # Store original activities
    original_activities = deepcopy(activities)
    
    # Replace activities with mock data
    activities.clear()
    activities.update(mock_activities)
    
    yield TestClient(app)
    
    # Restore original activities after test
    activities.clear()
    activities.update(original_activities)
