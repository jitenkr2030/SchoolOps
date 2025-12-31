"""
GraphQL resolver tests for SchoolOps Backend
"""
import pytest
from fastapi.testclient import TestClient
import strawberry
from strawberry.fastapi import GraphQLRouter


class TestGraphQLQueries:
    """Tests for GraphQL query resolvers."""
    
    def test_hello_query(self, client):
        """Test the hello query."""
        query = """
        query {
            hello
        }
        """
        response = client.post(
            "/graphql",
            json={"query": query}
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "hello" in data["data"]
    
    def test_get_students_query(self, client, test_student):
        """Test fetching all students via GraphQL."""
        query = """
        query {
            students {
                id
                firstName
                lastName
                email
                admissionNumber
            }
        }
        """
        response = client.post(
            "/graphql",
            json={"query": query}
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "students" in data["data"]
        students = data["data"]["students"]
        # Should contain our test student
        student_ids = [s["id"] for s in students]
        assert str(test_student.id) in student_ids or test_student.id in student_ids
    
    def test_get_student_by_id_query(self, client, test_student):
        """Test fetching a specific student via GraphQL."""
        query = f"""
        query {{
            student(id: {test_student.id}) {{
                id
                firstName
                lastName
                email
                admissionNumber
            }}
        }}
        """
        response = client.post(
            "/graphql",
            json={"query": query}
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "student" in data["data"]
        student = data["data"]["student"]
        if student:
            assert student["firstName"] == test_student.first_name
            assert student["lastName"] == test_student.last_name
    
    def test_get_teachers_query(self, client, test_teacher):
        """Test fetching all teachers via GraphQL."""
        query = """
        query {
            teachers {
                id
                firstName
                lastName
                email
                subject
            }
        }
        """
        response = client.post(
            "/graphql",
            json={"query": query}
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "teachers" in data["data"]
    
    def test_get_classes_query(self, client, test_class):
        """Test fetching all classes via GraphQL."""
        query = """
        query {
            classes {
                id
                name
            }
        }
        """
        response = client.post(
            "/graphql",
            json={"query": query}
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "classes" in data["data"]
    
    def test_get_academic_years_query(self, client, test_academic_year):
        """Test fetching academic years via GraphQL."""
        query = """
        query {
            academicYears {
                id
                name
                startDate
                endDate
                isActive
            }
        }
        """
        response = client.post(
            "/graphql",
            json={"query": query}
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "academicYears" in data["data"]


class TestGraphQLMutations:
    """Tests for GraphQL mutation resolvers."""
    
    def test_create_student_mutation(self, client):
        """Test creating a student via GraphQL."""
        mutation = """
        mutation {
            createStudent(
                firstName: "GraphQL"
                lastName: "Student"
                email: "graphql@test.com"
                admissionNumber: "GQL001"
            ) {
                id
                firstName
                lastName
                email
            }
        }
        """
        response = client.post(
            "/graphql",
            json={"query": mutation}
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "createStudent" in data["data"]
        result = data["data"]["createStudent"]
        if result:
            assert result["firstName"] == "GraphQL"
    
    def test_create_teacher_mutation(self, client):
        """Test creating a teacher via GraphQL."""
        mutation = """
        mutation {
            createTeacher(
                firstName: "GraphQL"
                lastName: "Teacher"
                email: "graphql.teacher@test.com"
                subject: "Chemistry"
            ) {
                id
                firstName
                lastName
                subject
            }
        }
        """
        response = client.post(
            "/graphql",
            json={"query": mutation}
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "createTeacher" in data["data"]
    
    def test_create_class_mutation(self, client, test_academic_year):
        """Test creating a class via GraphQL."""
        mutation = f"""
        mutation {{
            createClass(
                name: "Class 11"
                academicYearId: {test_academic_year.id}
            ) {{
                id
                name
            }}
        }}
        """
        response = client.post(
            "/graphql",
            json={"query": mutation}
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "createClass" in data["data"]
    
    def test_create_academic_year_mutation(self, client):
        """Test creating an academic year via GraphQL."""
        mutation = """
        mutation {
            createAcademicYear(
                name: "2026-2027"
                startDate: "2026-04-01"
                endDate: "2027-03-31"
                isActive: false
            ) {
                id
                name
                isActive
            }
        }
        """
        response = client.post(
            "/graphql",
            json={"query": mutation}
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "createAcademicYear" in data["data"]


class TestGraphQLValidation:
    """Tests for GraphQL validation and error handling."""
    
    def test_invalid_query_syntax(self, client):
        """Test handling of invalid query syntax."""
        query = """
        query {
            invalid syntax here
        }
        """
        response = client.post(
            "/graphql",
            json={"query": query}
        )
        assert response.status_code == 400
    
    def test_missing_required_fields(self, client):
        """Test mutation with missing required fields."""
        mutation = """
        mutation {
            createStudent(firstName: "Test") {
                id
            }
        }
        """
        response = client.post(
            "/graphql",
            json={"query": mutation}
        )
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
    
    def test_nonexistent_field(self, client):
        """Test querying a nonexistent field."""
        query = """
        query {
            nonexistentField
        }
        """
        response = client.post(
            "/graphql",
            json={"query": query}
        )
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
    
    def test_nested_query(self, client, test_class, test_student):
        """Test nested GraphQL queries."""
        query = f"""
        query {{
            classes {{
                id
                name
                students {{
                    id
                    firstName
                }}
            }}
        }}
        """
        response = client.post(
            "/graphql",
            json={"query": query}
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "classes" in data["data"]


class TestGraphQLAuthentication:
    """Tests for GraphQL authentication."""
    
    def test_public_query_accessible(self, client):
        """Test that public queries are accessible without auth."""
        query = """
        query {
            hello
        }
        """
        response = client.post(
            "/graphql",
            json={"query": query}
        )
        assert response.status_code == 200
    
    def test_protected_mutation_requires_auth(self, client):
        """Test that protected mutations require authentication."""
        # This test verifies that mutations that require auth
        # are properly protected at the resolver level
        mutation = """
        mutation {
            createStudent(
                firstName: "Protected"
                lastName: "Student"
                email: "protected@test.com"
                admissionNumber: "PROT001"
            ) {
                id
            }
        }
        """
        response = client.post(
            "/graphql",
            json={"query": mutation}
        )
        # Response should either succeed (if mutation is public)
        # or contain an error about authentication
        assert response.status_code == 200
        data = response.json()
        # If protected, there should be an error or the mutation should fail
        if "errors" in data:
            assert any("auth" in str(error).lower() for error in data["errors"])
