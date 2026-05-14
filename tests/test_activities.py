import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities with correct structure."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Art Workshop" in data
    
    def test_get_activities_contains_required_fields(self, client):
        """Test that each activity has all required fields."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)
    
    def test_get_activities_participants_are_strings(self, client):
        """Test that participants in each activity are email strings."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_details in data.values():
            for participant in activity_details["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email validation


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "david@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "david@mergington.edu" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "david@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_duplicate_student(self, client):
        """Test that signing up a student twice raises 400 error."""
        # alice@mergington.edu is already signed up for Chess Club
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "alice@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test that signing up for a non-existent activity raises 404 error."""
        response = client.post(
            "/activities/Nonexistent%20Club/signup",
            params={"email": "eve@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_empty_participants_activity(self, client):
        """Test signing up for an activity with no existing participants."""
        response = client.post(
            "/activities/Art%20Workshop/signup",
            params={"email": "frank@mergington.edu"}
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "frank@mergington.edu" in activities_data["Art Workshop"]["participants"]
    
    def test_signup_multiple_students_same_activity(self, client):
        """Test signing up multiple different students for the same activity."""
        # Sign up first student
        response1 = client.post(
            "/activities/Art%20Workshop/signup",
            params={"email": "grace@mergington.edu"}
        )
        assert response1.status_code == 200
        
        # Sign up second student
        response2 = client.post(
            "/activities/Art%20Workshop/signup",
            params={"email": "henry@mergington.edu"}
        )
        assert response2.status_code == 200
        
        # Verify both were added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        participants = activities_data["Art Workshop"]["participants"]
        assert "grace@mergington.edu" in participants
        assert "henry@mergington.edu" in participants


class TestUnregisterParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint."""
    
    def test_unregister_success(self, client):
        """Test successful unregistration of a participant."""
        response = client.delete(
            "/activities/Chess%20Club/participants",
            params={"email": "alice@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "alice@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_participant(self, client):
        """Test that unregistering a non-existent participant raises 404 error."""
        response = client.delete(
            "/activities/Chess%20Club/participants",
            params={"email": "unknown@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test that unregistering from a non-existent activity raises 404 error."""
        response = client.delete(
            "/activities/Fake%20Club/participants",
            params={"email": "alice@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_all_participants(self, client):
        """Test unregistering all participants from an activity."""
        # Unregister both participants from Chess Club
        response1 = client.delete(
            "/activities/Chess%20Club/participants",
            params={"email": "alice@mergington.edu"}
        )
        assert response1.status_code == 200
        
        response2 = client.delete(
            "/activities/Chess%20Club/participants",
            params={"email": "bob@mergington.edu"}
        )
        assert response2.status_code == 200
        
        # Verify activity now has no participants
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert activities_data["Chess Club"]["participants"] == []


class TestSignupAndUnregisterFlow:
    """Tests for combined signup and unregister workflows."""
    
    def test_signup_then_unregister(self, client):
        """Test signing up and then unregistering the same student."""
        email = "iris@mergington.edu"
        activity = "Programming%20Class"
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify signup succeeded
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Programming Class"]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Verify unregister succeeded
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data["Programming Class"]["participants"]
    
    def test_signup_unregister_signup_again(self, client):
        """Test signing up, unregistering, and signing up again."""
        email = "jack@mergington.edu"
        activity = "Art%20Workshop"
        
        # First signup
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Second signup (should succeed since we unregistered)
        response3 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response3.status_code == 200
        
        # Verify final state
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Art Workshop"]["participants"]
