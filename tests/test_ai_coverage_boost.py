"""
Targeted tests to push coverage from 85% to 95%+
Focus on remaining uncovered lines in critical modules
"""

from unittest.mock import Mock, patch

import pytest

from app.services.ai import AIProvider


class TestAIServiceAdvancedCoverage:
    """Advanced AI service tests to cover remaining uncovered code"""

    @pytest.mark.asyncio
    async def test_classify_openai_success(self):
        """Test OpenAI classification success path"""
        provider = "OpenAI"
        api_key = "test-key"

        with (
            patch("app.services.ai.settings.provider", provider),
            patch("app.services.ai.settings.openai_api_key", api_key),
        ):
            # Mock successful OpenAI response
            with patch("httpx.AsyncClient.post") as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                response_content = '{"category": "Produtivo", "rationale": "Test"}'
                mock_response.json.return_value = {
                    "choices": [{"message": {"content": response_content}}],
                    "usage": {"total_tokens": 50},
                }
                mock_post.return_value = mock_response

                ai_provider = AIProvider()
                result = await ai_provider.classify("Preciso de ajuda urgente")

                assert result["category"] == "Produtivo"
                assert "confidence" in result

    @pytest.mark.asyncio
    async def test_classify_huggingface_provider(self):
        """Test classification with HuggingFace provider"""
        with patch("app.services.ai.settings.provider", "HF"):
            ai_provider = AIProvider()

            # Mock the HuggingFace method
            mock_return = {
                "category": "Produtivo",
                "confidence": 0.85,
                "rationale": "HF classification",
            }
            with patch.object(
                ai_provider, "_classify_huggingface", return_value=mock_return
            ):
                result = await ai_provider.classify("Test text")
                assert result["category"] == "Produtivo"

    @pytest.mark.asyncio
    async def test_generate_reply_openai(self):
        """Test reply generation with OpenAI"""
        with (
            patch("app.services.ai.settings.provider", "OpenAI"),
            patch("app.services.ai.settings.openai_api_key", "test-key"),
        ):
            # Mock successful OpenAI API response for reply generation
            with patch("httpx.AsyncClient.post") as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "choices": [{"message": {"content": "OpenAI generated reply"}}],
                    "usage": {"total_tokens": 25},
                }
                mock_post.return_value = mock_response

                ai_provider = AIProvider()
                result = await ai_provider.generate_reply("Test", "Produtivo", "formal")

                # Should return some form of reply (may include template formatting)
                assert isinstance(result, str)
                assert len(result) > 0

    @pytest.mark.asyncio
    async def test_generate_reply_huggingface(self):
        """Test reply generation with HuggingFace provider"""
        with patch("app.services.ai.settings.provider", "HF"):
            ai_provider = AIProvider()

            mock_reply = "HF generated reply"
            with patch.object(
                ai_provider, "_generate_reply_huggingface", return_value=mock_reply
            ):
                result = await ai_provider.generate_reply("Test", "Produtivo", "formal")
                assert result == mock_reply

    @pytest.mark.asyncio
    async def test_refine_reply_openai(self):
        """Test reply refinement with OpenAI provider"""
        with patch("app.services.ai.settings.provider", "OpenAI"):
            ai_provider = AIProvider()

            mock_refined = "OpenAI refined reply"
            with patch.object(
                ai_provider, "_refine_reply_openai", return_value=mock_refined
            ):
                result = await ai_provider.refine_reply("Original reply", "formal")
                assert result == mock_refined

    @pytest.mark.asyncio
    async def test_refine_reply_huggingface(self):
        """Test reply refinement with HuggingFace provider"""
        with patch("app.services.ai.settings.provider", "HF"):
            ai_provider = AIProvider()

            mock_refined = "HF refined reply"
            with patch.object(
                ai_provider, "_refine_reply_huggingface", return_value=mock_refined
            ):
                result = await ai_provider.refine_reply("Original reply", "casual")
                assert result == mock_refined

    @pytest.mark.asyncio
    async def test_openai_api_error_handling(self):
        """Test OpenAI API error handling"""
        provider = "OpenAI"
        api_key = "test-key"

        with (
            patch("app.services.ai.settings.provider", provider),
            patch("app.services.ai.settings.openai_api_key", api_key),
        ):
            # Mock API error response
            with patch("httpx.AsyncClient.post") as mock_post:
                mock_response = Mock()
                mock_response.status_code = 500
                mock_response.json.return_value = {"error": {"message": "Server error"}}
                mock_response.content = b'{"error": {"message": "Server error"}}'
                mock_post.return_value = mock_response

                ai_provider = AIProvider()
                result = await ai_provider.classify("Test email")

                # Should fallback to heuristics
                assert result["meta"]["fallback"] is True

    @pytest.mark.asyncio
    async def test_openai_timeout_handling(self):
        """Test OpenAI API timeout handling"""
        provider = "OpenAI"
        api_key = "test-key"

        with (
            patch("app.services.ai.settings.provider", provider),
            patch("app.services.ai.settings.openai_api_key", api_key),
        ):
            # Mock timeout exception
            with patch(
                "httpx.AsyncClient.post", side_effect=Exception("Request timeout")
            ):
                ai_provider = AIProvider()
                result = await ai_provider.classify("Test email")

                # Should fallback to heuristics
                assert result["meta"]["fallback"] is True

    @pytest.mark.asyncio
    async def test_openai_invalid_json_response(self):
        """Test OpenAI API with invalid JSON response"""
        provider = "OpenAI"
        api_key = "test-key"

        with (
            patch("app.services.ai.settings.provider", provider),
            patch("app.services.ai.settings.openai_api_key", api_key),
        ):
            # Mock response that will cause JSON parsing issues
            with patch("httpx.AsyncClient.post") as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                # This should cause JSON parsing to fail when trying to extract category
                mock_response.json.return_value = {
                    "choices": [{"message": {"content": "{invalid: json structure"}}]
                }
                mock_post.return_value = mock_response

                ai_provider = AIProvider()
                result = await ai_provider.classify("Test email")

                # Should handle JSON parsing gracefully
                # Either returns valid result or falls back to heuristics
                assert "category" in result
                assert result["category"] in ["Produtivo", "Improdutivo"]

    def test_ai_provider_initialization(self):
        """Test AIProvider initialization"""
        ai_provider = AIProvider()
        assert ai_provider is not None

    @pytest.mark.asyncio
    async def test_classify_with_different_providers(self):
        """Test classification works with different providers"""
        # Test OpenAI provider
        with (
            patch("app.services.ai.settings.provider", "OpenAI"),
            patch("app.services.ai.settings.openai_api_key", "test-key"),
        ):
            with patch("httpx.AsyncClient.post") as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "choices": [
                        {
                            "message": {
                                "content": (
                                    '{"category": "Produtivo", "rationale": "Test"}'
                                )
                            }
                        }
                    ],
                    "usage": {"total_tokens": 50},
                }
                mock_post.return_value = mock_response

                ai_provider = AIProvider()
                result = await ai_provider.classify("Test urgent email")
                assert result["category"] in ["Produtivo", "Improdutivo"]

        # Test HuggingFace provider fallback
        with patch("app.services.ai.settings.provider", "HF"):
            ai_provider = AIProvider()
            result = await ai_provider.classify("Test email")
            # Should return valid classification (likely heuristic fallback)
            assert result["category"] in ["Produtivo", "Improdutivo"]

    @pytest.mark.asyncio
    async def test_generate_reply_error_fallback(self):
        """Test reply generation error handling"""
        with patch("app.services.ai.settings.provider", "OpenAI"):
            ai_provider = AIProvider()

            # Mock method that raises exception
            with patch.object(
                ai_provider,
                "_generate_reply_openai",
                side_effect=Exception("API error"),
            ):
                result = await ai_provider.generate_reply("Test", "Produtivo", "formal")
                # Should return fallback reply or handle gracefully
                assert isinstance(result, str)
