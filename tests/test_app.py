import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    def test_get_activities_returns_all_activities(self):
        """Test retrieving all activities"""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class", 
                              "Basketball", "Track and Field", "Drama Club", 
                              "Visual Arts", "Debate Team", "Robotics Club"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity in expected_activities:
            assert activity in data

    def test_activity_has_correct_structure(self):
        """Test that activities have required fields"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        activity = activities["Chess Club"]
        
        # Assert
        for field in required_fields:
            assert field in activity
        assert isinstance(activity["participants"], list)


class TestSignupEndpoint:
    def test_student_can_signup_for_activity(self):
        """Test successful signup for an activity"""
        # Arrange
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]

    def test_duplicate_signup_is_rejected(self):
        """Test that duplicate signups return 400 error"""
        # Arrange
        email = "duplicate@mergington.edu"
        activity_name = "Programming Class"
        
        # Act - First signup succeeds
        response1 = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Act - Duplicate signup fails
        response2 = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_for_nonexistent_activity_fails(self):
        """Test signup for non-existent activity returns 404"""
        # Arrange
        email = "student@mergington.edu"
        activity_name = "Nonexistent Activity"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_participant_is_added_to_activity_list(self):
        """Test that signup adds participant to activity's participant list"""
        # Arrange
        email = "verify@mergington.edu"
        activity_name = "Gym Class"
        
        # Act
        client.post(f"/activities/{activity_name}/signup?email={email}")
        response = client.get("/activities")
        
        # Assert
        activities = response.json()
        assert email in activities[activity_name]["participants"]


class TestUnregisterEndpoint:
    def test_student_can_unregister_from_activity(self):
        """Test successful unregistration from an activity"""
        # Arrange
        email = "unregister@mergington.edu"
        activity_name = "Chess Club"
        
        # Act - Sign up first
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Act - Unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_participant_is_removed_from_activity_list(self):
        """Test that unregister removes participant from activity"""
        # Arrange
        email = "remove@mergington.edu"
        activity_name = "Programming Class"
        
        # Act - Sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Act - Unregister
        client.delete(f"/activities/{activity_name}/unregister?email={email}")
        
        # Act - Verify removal
        response = client.get("/activities")
        
        # Assert
        activities = response.json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_nonexistent_student_fails(self):
        """Test unregistering a non-signed-up student returns 400"""
        # Arrange
        email = "notregistered@mergington.edu"
        activity_name = "Chess Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_from_nonexistent_activity_fails(self):
        """Test unregistering from non-existent activity returns 404"""
        # Arrange
        email = "student@mergington.edu"
        activity_name = "Nonexistent Activity"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestRootEndpoint:
    def test_root_redirects_to_index_page(self):
        """Test that root path redirects to static index page"""
        # Arrange
        expected_redirect = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect
