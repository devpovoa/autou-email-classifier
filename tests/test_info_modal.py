"""
Tests for the info modal functionality in the web interface.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestInfoModal:
    """Test the info modal functionality."""
    
    def test_main_page_loads_with_info_button(self):
        """Test that the main page loads and contains the info button."""
        response = client.get("/")
        assert response.status_code == 200
        
        # Check if the info button HTML is present
        content = response.text
        assert 'title="Informações do Sistema"' in content
        assert '$store.ui.toggleInfo()' in content
        
    def test_info_modal_html_structure(self):
        """Test that the info modal HTML structure is present."""
        response = client.get("/")
        assert response.status_code == 200
        
        content = response.text
        
        # Check for modal structure
        assert '$store.ui.showInfo' in content
        assert 'AutoU - Classificador de E-mails' in content
        assert 'Informações do Sistema' in content
        
        # Check for system features
        assert 'IA Avançada' in content
        assert 'OpenAI GPT-4o-mini' in content
        assert 'Segurança JWT' in content
        assert 'Multi-formato' in content
        assert 'Alto Desempenho' in content
        
        # Check for API information
        assert '/docs' in content
        assert '/health' in content
        assert 'JWT + Rate Limiting' in content
        
        # Check for technical information
        assert 'v1.0.0' in content
        assert 'FastAPI + AlpineJS' in content
        assert '87% (167 testes)' in content
        assert 'Docker Ready' in content
        
    def test_alpine_store_configuration(self):
        """Test that Alpine.js store configuration is present."""
        response = client.get("/")
        assert response.status_code == 200
        
        content = response.text
        
        # Check for Alpine store configuration
        assert "Alpine.store('ui'" in content
        assert 'showInfo: false' in content
        assert 'toggleInfo()' in content
        assert 'closeInfo()' in content
        assert 'openInfo()' in content
        
    def test_modal_accessibility(self):
        """Test that the modal has proper accessibility attributes."""
        response = client.get("/")
        assert response.status_code == 200
        
        content = response.text
        
        # Check for accessibility features
        assert '@click.self="$store.ui.closeInfo()"' in content  # Click outside to close
        assert 'x-transition' in content  # Smooth transitions
        assert 'z-50' in content  # Proper z-index
        
    def test_modal_close_functionality(self):
        """Test that the modal has multiple ways to close."""
        response = client.get("/")
        assert response.status_code == 200
        
        content = response.text
        
        # Check for close button
        assert '$store.ui.closeInfo()' in content
        # Check for click outside to close
        assert '@click.self="$store.ui.closeInfo()"' in content
        # Check for ESC key (would be handled by Alpine.js)
        
    def test_responsive_design_classes(self):
        """Test that the modal has responsive design classes."""
        response = client.get("/")
        assert response.status_code == 200
        
        content = response.text
        
        # Check for responsive classes
        assert 'max-w-2xl' in content  # Maximum width
        assert 'max-h-[90vh]' in content  # Maximum height
        assert 'overflow-y-auto' in content  # Scrollable content
        assert 'md:grid-cols-2' in content  # Responsive grid
        
    def test_dark_mode_support(self):
        """Test that the modal supports dark mode."""
        response = client.get("/")
        assert response.status_code == 200
        
        content = response.text
        
        # Check for dark mode classes
        assert 'dark:bg-gray-800' in content
        assert 'dark:text-white' in content
        assert 'dark:border-gray-700' in content
        assert 'dark:text-gray-400' in content


class TestInfoModalContent:
    """Test the content of the info modal."""
    
    def test_system_status_section(self):
        """Test the system status section content."""
        response = client.get("/")
        content = response.text
        
        assert 'Sistema Operacional' in content
        assert 'Todos os serviços estão funcionando normalmente' in content
        assert 'animate-pulse' in content  # Status indicator animation
        
    def test_features_section(self):
        """Test the features section content."""
        response = client.get("/")
        content = response.text
        
        features = [
            'IA Avançada',
            'Segurança JWT', 
            'Multi-formato',
            'Alto Desempenho'
        ]
        
        for feature in features:
            assert feature in content
            
    def test_api_information_section(self):
        """Test the API information section."""
        response = client.get("/")
        content = response.text
        
        assert 'API REST' in content
        assert 'Documentação' in content
        assert 'Health Check' in content
        assert 'Autenticação' in content
        
    def test_technical_information_section(self):
        """Test the technical information section."""
        response = client.get("/")
        content = response.text
        
        technical_info = [
            'Versão:',
            'Framework:',
            'Cobertura de Testes:',
            'Containerização:'
        ]
        
        for info in technical_info:
            assert info in content
            
    def test_links_are_present(self):
        """Test that important links are present in the modal."""
        response = client.get("/")
        content = response.text
        
        # API documentation link
        assert 'href="/docs"' in content
        assert 'target="_blank"' in content
        
        # Health check link  
        assert 'href="/health"' in content
