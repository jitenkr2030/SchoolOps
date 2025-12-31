"""
Unit tests for AI NLP and Chatbot Services
"""
import pytest
from app.routers.nlp import (
    process_chatbot_query,
    analyze_sentiment,
    translate_text,
    summarize_text,
    extract_intent,
    generate_auto_response
)


class TestChatbotQueryProcessing:
    """Tests for Chatbot Query Processing."""
    
    def test_process_attendance_query(self, sample_chatbot_query, mock_nlp_model):
        """Test processing attendance-related queries."""
        query = sample_chatbot_query["queries"][0]
        
        result = process_chatbot_query(query)
        
        assert "intent" in result
        assert "entities" in result
        assert "response" in result
        assert result["intent"] == "attendance_inquiry"
    
    def test_process_fee_query(self, sample_chatbot_query, mock_nlp_model):
        """Test processing fee-related queries."""
        query = sample_chatbot_query["queries"][1]
        
        result = process_chatbot_query(query)
        
        assert "intent" in result
        assert result["intent"] == "fee_inquiry"
    
    def test_process_homework_query(self, sample_chatbot_query, mock_nlp_model):
        """Test processing homework-related queries."""
        query = sample_chatbot_query["queries"][2]
        
        result = process_chatbot_query(query)
        
        assert "intent" in result
        assert result["intent"] == "homework_inquiry"
    
    def test_multilingual_support(self, mock_nlp_model):
        """Test multilingual query processing."""
        queries = [
            "What is my child's attendance?",  # English
            "मेरे बच्चे की उपस्थिति क्या है?",  # Hindi
        ]
        
        for query in queries:
            result = process_chatbot_query(query)
            assert "response" in result
            assert result["response"] != ""
    
    def test_unknown_query_handling(self, mock_nlp_model):
        """Test handling of unknown queries."""
        query = "What is the meaning of life?"
        
        result = process_chatbot_query(query)
        
        assert "intent" in result
        assert result["intent"] == "unknown"
        assert "fallback_response" in result


class TestSentimentAnalysis:
    """Tests for Sentiment Analysis."""
    
    def test_positive_sentiment(self, mock_nlp_model):
        """Test positive sentiment detection."""
        text = "The school is excellent! My child loves it."
        
        result = analyze_sentiment(text)
        
        assert result["sentiment"] in ["positive", "neutral"]
        assert "score" in result
        assert 0.0 <= result["score"] <= 1.0
    
    def test_negative_sentiment(self, mock_nlp_model):
        """Test negative sentiment detection."""
        text = "Very disappointed with the school management."
        
        result = analyze_sentiment(text)
        
        assert result["sentiment"] in ["negative", "neutral"]
    
    def test_neutral_sentiment(self, mock_nlp_model):
        """Test neutral sentiment detection."""
        text = "The school closes at 4 PM."
        
        result = analyze_sentiment(text)
        
        assert result["sentiment"] == "neutral"
    
    def test_sentiment_score_range(self, mock_nlp_model):
        """Test sentiment score range."""
        texts = [
            "Excellent school!",
            "Average school.",
            "Poor experience.",
        ]
        
        for text in texts:
            result = analyze_sentiment(text)
            assert 0.0 <= result["score"] <= 1.0


class TestTextTranslation:
    """Tests for Text Translation."""
    
    def test_translation_to_hindi(self, mock_nlp_model):
        """Test translation to Hindi."""
        text = "What is the fee structure?"
        
        result = translate_text(text, target_lang="Hindi")
        
        assert "translated_text" in result
        assert "source_language" in result
        assert "target_language" in result
        assert result["target_language"] == "Hindi"
    
    def test_translation_preserves_meaning(self, mock_nlp_model):
        """Test that translation preserves meaning."""
        text = "Your child scored 85 marks in Mathematics."
        
        result = translate_text(text, target_lang="Tamil")
        
        assert result["translated_text"] != text
        assert "85" in result["translated_text"]  # Numbers should be preserved
    
    def test_supported_languages(self, mock_nlp_model):
        """Test supported language detection."""
        result = translate_text("Hello", target_lang="Spanish")
        
        assert result["target_language"] == "Spanish"


class TestTextSummarization:
    """Tests for Text Summarization."""
    
    def test_summarization_shortens_text(self, mock_nlp_model):
        """Test that summarization shortens text."""
        long_text = """
        The parent-teacher meeting will be held on 15th October 2024 at 10:00 AM 
        in the school auditorium. All parents are requested to attend the meeting 
        to discuss the academic progress of their children. The agenda includes 
        discussion on examination results, attendance records, and upcoming events. 
        Please ensure timely arrival and bring the previous progress report cards.
        """
        
        result = summarize_text(long_text)
        
        assert len(result["summary"]) < len(long_text)
        assert "summary" in result
    
    def test_max_length_respected(self, mock_nlp_model):
        """Test that max_length parameter is respected."""
        text = "This is a long text that needs to be summarized."
        
        result = summarize_text(text, max_length=10)
        
        assert len(result["summary"].split()) <= 10
    
    def test_key_points_preserved(self, mock_nlp_model):
        """Test that key points are preserved in summary."""
        text = """
        Important Notice: School will remain closed on 26th January 2024 
        (Friday) on account of Republic Day. All students should take note 
        of this holiday. Regular classes will resume on 27th January 2024.
        """
        
        result = summarize_text(text)
        
        # Summary should mention the holiday
        assert "26th" in result["summary"] or "Republic Day" in result["summary"] or "closed" in result["summary"].lower()


class TestIntentExtraction:
    """Tests for Intent Extraction."""
    
    def test_attendance_intent(self):
        """Test attendance intent extraction."""
        text = "What was my child's attendance last week?"
        
        result = extract_intent(text)
        
        assert result["intent"] == "attendance_inquiry"
        assert "entities" in result
        assert "time_period" in result["entities"]
    
    def test_fee_intent(self):
        """Test fee intent extraction."""
        text = "When is the next fee installment due?"
        
        result = extract_intent(text)
        
        assert result["intent"] == "fee_inquiry"
        assert "entities" in result
        assert "fee_type" in result["entities"]
    
    def test_grade_intent(self):
        """Test grade intent extraction."""
        text = "What grades did my child get in the last exam?"
        
        result = extract_intent(text)
        
        assert result["intent"] == "grade_inquiry"
    
    def test_multiple_intents(self):
        """Test queries with multiple possible intents."""
        text = "What is my child's attendance and when are fees due?"
        
        result = extract_intent(text)
        
        assert "primary_intent" in result
        assert "secondary_intent" in result


class TestAutoResponse:
    """Tests for Auto Response Generation."""
    
    def test_response_for_attendance(self, mock_nlp_model):
        """Test auto response for attendance inquiry."""
        context = {
            "intent": "attendance_inquiry",
            "student_name": "John Doe",
            "attendance_percentage": 92
        }
        
        result = generate_auto_response(context)
        
        assert "response" in result
        assert "John" in result["response"] or "attendance" in result["response"].lower()
    
    def test_response_for_fees(self, mock_nlp_model):
        """Test auto response for fee inquiry."""
        context = {
            "intent": "fee_inquiry",
            "student_name": "Jane Smith",
            "next_due_date": "2024-11-30",
            "amount_due": 5000
        }
        
        result = generate_auto_response(context)
        
        assert "response" in result
        assert "5000" in result["response"] or "Rs" in result["response"]
    
    def test_response_tone(self, mock_nlp_model):
        """Test that responses maintain professional tone."""
        context = {
            "intent": "general_inquiry",
            "student_name": "Test Student"
        }
        
        result = generate_auto_response(context)
        
        # Response should be polite and professional
        assert any(word in result["response"].lower() for word in ["please", "thank you", "regards"])
    
    def test_response_with_parent_name(self, mock_nlp_model):
        """Test response includes parent name."""
        context = {
            "intent": "general_inquiry",
            "parent_name": "Mr. Sharma"
        }
        
        result = generate_auto_response(context)
        
        assert "Sharma" in result["response"] or "Mr." in result["response"]
