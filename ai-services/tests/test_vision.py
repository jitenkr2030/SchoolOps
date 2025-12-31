"""
Unit tests for AI Vision and Document Processing Services
"""
import pytest
from app.routers.vision import (
    extract_text_from_image,
    verify_document,
    process_invoice,
    grade_handwritten_work,
    extract_student_info
)


class TestOCRTextExtraction:
    """Tests for OCR Text Extraction."""
    
    def test_extract_text_from_image(self, mock_vision_model, sample_document_image):
        """Test basic text extraction from image."""
        result = extract_text_from_image(sample_document_image["image_base64"])
        
        assert "extracted_text" in result
        assert "confidence" in result
        assert 0.0 <= result["confidence"] <= 1.0
    
    def test_extracted_text_completeness(self, mock_vision_model):
        """Test that extracted text is complete."""
        image_data = "base64_encoded_image"
        
        result = extract_text_from_image(image_data)
        
        assert result["extracted_text"] is not None
        assert isinstance(result["extracted_text"], str)
    
    def test_multiple_language_support(self, mock_vision_model):
        """Test OCR for multiple languages."""
        for lang in ["English", "Hindi", "Tamil"]:
            result = extract_text_from_image("base64_data", language=lang)
            
            assert "extracted_text" in result
            assert "language_detected" in result
    
    def test_handwriting_recognition(self, mock_vision_model):
        """Test handwritten text recognition."""
        handwritten_image = "base64_encoded_handwriting"
        
        result = extract_text_from_image(handwritten_image, is_handwritten=True)
        
        assert "extracted_text" in result
        assert "handwriting_confidence" in result


class TestDocumentVerification:
    """Tests for Document Verification."""
    
    def test_verify_valid_document(self, mock_vision_model, sample_document_image):
        """Test verification of valid document."""
        result = verify_document(sample_document_image["document_type"], sample_document_image["image_base64"])
        
        assert "is_valid" in result
        assert "confidence" in result
        assert "verification_details" in result
    
    def test_invalid_document_detection(self, mock_vision_model):
        """Test detection of invalid/tampered documents."""
        result = verify_document("id_card", "suspicious_document_base64")
        
        assert "is_valid" in result
        if not result["is_valid"]:
            assert "reason" in result
    
    def test_id_card_verification_fields(self, mock_vision_model):
        """Test ID card verification for required fields."""
        result = verify_document("id_card", "id_card_image_base64")
        
        required_fields = ["name", "dob", "photo_id_number"]
        for field in required_fields:
            assert field in result.get("extracted_fields", {})
    
    def test_certificate_verification(self, mock_vision_model):
        """Test verification of certificates."""
        result = verify_document("certificate", "certificate_image_base64")
        
        assert "issue_date" in result.get("extracted_fields", {})
        assert "expiry_date" in result.get("extracted_fields", {})


class TestInvoiceProcessing:
    """Tests for Invoice Processing."""
    
    def test_process_invoice(self, mock_vision_model, sample_document_image):
        """Test invoice processing and data extraction."""
        result = process_invoice(sample_document_image["image_base64"])
        
        assert "invoice_number" in result
        assert "date" in result
        assert "vendor" in result
        assert "amount" in result
        assert "line_items" in result
    
    def test_invoice_amount_extraction(self, mock_vision_model):
        """Test invoice amount extraction."""
        invoice_data = "base64_invoice_image"
        
        result = process_invoice(invoice_data)
        
        assert "total_amount" in result
        assert "tax_amount" in result
        assert result["total_amount"] > 0
    
    def test_invoice_vendor_extraction(self, mock_vision_model):
        """Test vendor information extraction."""
        result = process_invoice("invoice_image")
        
        assert "vendor" in result
        assert "vendor_name" in result["vendor"]
        assert "vendor_address" in result["vendor"]
    
    def test_invoice_line_items(self, mock_vision_model):
        """Test invoice line item extraction."""
        result = process_invoice("invoice_image")
        
        assert "line_items" in result
        assert len(result["line_items"]) > 0
        for item in result["line_items"]:
            assert "description" in item
            assert "quantity" in item
            assert "unit_price" in item
            assert "total" in item


class TestHandwrittenGrading:
    """Tests for Handwritten Work Grading."""
    
    def test_grade_handwritten_work(self, mock_vision_model):
        """Test grading handwritten work."""
        result = grade_handwritten_work(
            image_data="handwritten_answer_base64",
            rubric={
                "correctness": 40,
                "completeness": 30,
                "presentation": 30
            }
        )
        
        assert "total_score" in result
        assert "max_score" in result
        assert "breakdown" in result
        assert "feedback" in result
    
    def test_rubric_based_scoring(self, mock_vision_model):
        """Test scoring based on rubric criteria."""
        result = grade_handwritten_work(
            image_data="handwritten_work",
            rubric={
                "accuracy": 50,
                "understanding": 30,
                "presentation": 20
            }
        )
        
        for criterion, max_score in result["rubric"].items():
            assert criterion in result["breakdown"]
            assert result["breakdown"][criterion] <= max_score
    
    def test_feedback_generation(self, mock_vision_model):
        """Test feedback generation for handwritten work."""
        result = grade_handwritten_work(
            image_data="handwritten_essay",
            rubric={"content": 50, "grammar": 30, "style": 20}
        )
        
        assert "feedback" in result
        assert isinstance(result["feedback"], str)
        assert len(result["feedback"]) > 0
    
    def test_partial_credit(self, mock_vision_model):
        """Test partial credit calculation."""
        result = grade_handwritten_work(
            image_data="partial_answer",
            rubric={"problem": 100}
        )
        
        # Should handle partial answers
        assert result["total_score"] < result["max_score"] or result["total_score"] == result["max_score"]


class TestStudentInfoExtraction:
    """Tests for Student Information Extraction from Documents."""
    
    def test_extract_student_info_from_id(self, mock_vision_model):
        """Test extracting student info from ID card."""
        result = extract_student_info(
            document_type="id_card",
            image_data="student_id_base64"
        )
        
        assert "name" in result
        assert "student_id" in result
        assert "date_of_birth" in result
        assert "grade" in result or "class" in result
    
    def test_extract_from_admission_form(self, mock_vision_model):
        """Test extracting info from admission form."""
        result = extract_student_info(
            document_type="admission_form",
            image_data="admission_form_base64"
        )
        
        assert "parent_name" in result
        assert "contact_number" in result
        assert "address" in result
        assert "emergency_contact" in result
    
    def test_batch_student_creation(self, mock_vision_model):
        """Test batch student creation from multiple documents."""
        documents = [
            {"type": "id_card", "data": "base64_1"},
            {"type": "id_card", "data": "base64_2"},
            {"type": "id_card", "data": "base64_3"},
        ]
        
        results = []
        for doc in documents:
            result = extract_student_info(doc["type"], doc["data"])
            results.append(result)
        
        assert len(results) == 3
        for result in results:
            assert "name" in result
            assert "student_id" in result
    
    def test_data_validation(self, mock_vision_model):
        """Test extracted data validation."""
        result = extract_student_info(
            document_type="id_card",
            image_data="id_image"
        )
        
        # Validate data format
        if "date_of_birth" in result:
            # Should be in valid date format
            assert len(result["date_of_birth"]) == 10  # YYYY-MM-DD
        
        if "student_id" in result:
            assert result["student_id"].startswith("STU")
