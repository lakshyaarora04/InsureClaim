# 🤝 Contributing to LLM Document Query System

Thank you for your interest in contributing to our project! This document provides guidelines and information for contributors.

## 📋 **Table of Contents**

- [Getting Started](#-getting-started)
- [Development Setup](#-development-setup)
- [Code Style](#-code-style)
- [Testing](#-testing)
- [Pull Request Process](#-pull-request-process)
- [Issue Reporting](#-issue-reporting)
- [Code of Conduct](#-code-of-conduct)

## 🚀 **Getting Started**

### **Before You Start**

1. **Check Existing Issues**: Look through existing issues to see if your contribution is already being worked on
2. **Join Discussions**: Participate in GitHub Discussions to understand the project better
3. **Read Documentation**: Familiarize yourself with the project structure and architecture

### **Types of Contributions**

We welcome various types of contributions:

- 🐛 **Bug Fixes**: Fix issues and improve reliability
- ✨ **New Features**: Add new functionality and capabilities
- 📚 **Documentation**: Improve README, API docs, and code comments
- 🧪 **Tests**: Add or improve test coverage
- 🔧 **Refactoring**: Improve code structure and performance
- 🌐 **Translations**: Add support for new languages
- 💡 **Ideas**: Suggest new features or improvements

## 🛠️ **Development Setup**

### **1. Fork the Repository**

1. Go to [GitHub Repository](https://github.com/yourusername/llm-doc-query-system)
2. Click the "Fork" button in the top-right corner
3. Clone your forked repository:

```bash
git clone https://github.com/YOUR_USERNAME/llm-doc-query-system.git
cd llm-doc-query-system
```

### **2. Set Up Development Environment**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt  # if available
```

### **3. Set Up Pre-commit Hooks**

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install
```

## 📝 **Code Style**

### **Python Style Guide**

We follow **PEP 8** style guidelines:

```python
# ✅ Good
def calculate_confidence_score(age: int, gender: str) -> float:
    """Calculate confidence score based on age and gender."""
    base_score = 0.5
    
    if age > 18:
        base_score += 0.2
    
    if gender.lower() in ['male', 'female']:
        base_score += 0.1
    
    return min(base_score, 1.0)

# ❌ Bad
def calculate_confidence_score(age,gender):
    base_score=0.5
    if age>18:
        base_score+=0.2
    if gender.lower() in ['male','female']:
        base_score+=0.1
    return min(base_score,1.0)
```

### **Naming Conventions**

- **Functions**: `snake_case` (e.g., `calculate_confidence_score`)
- **Classes**: `PascalCase` (e.g., `InsuranceClaimRequest`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_CLAIM_AMOUNT`)
- **Variables**: `snake_case` (e.g., `patient_age`)

### **Documentation Standards**

#### **Docstrings**
```python
def evaluate_insurance_claim(request: InsuranceClaimRequest) -> InsuranceClaimResponse:
    """
    Evaluate an insurance claim based on multiple factors.
    
    Args:
        request (InsuranceClaimRequest): The claim request containing patient and claim details
        
    Returns:
        InsuranceClaimResponse: Evaluation result with approval status and reasoning
        
    Raises:
        ValueError: If request data is invalid
        ProcessingError: If evaluation fails
        
    Example:
        >>> request = InsuranceClaimRequest(claim_id="123", patient_age=35)
        >>> result = evaluate_insurance_claim(request)
        >>> print(result.approved)
        True
    """
    # Implementation here
```

#### **Type Hints**
```python
from typing import List, Optional, Dict, Any

def process_claims(claims: List[InsuranceClaimRequest]) -> Dict[str, InsuranceClaimResponse]:
    """Process multiple insurance claims."""
    pass
```

## 🧪 **Testing**

### **Running Tests**

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_webhook_server.py

# Run with coverage
python -m pytest --cov=backend --cov-report=html

# Run performance tests
python advanced_accuracy_test.py
```

### **Writing Tests**

#### **Test Structure**
```python
import pytest
from fastapi.testclient import TestClient
from webhook_server import app

client = TestClient(app)

class TestWebhookServer:
    """Test cases for webhook server functionality."""
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_document_qa_endpoint(self):
        """Test document Q&A endpoint."""
        payload = {
            "documents": "https://example.com/policy.pdf",
            "questions": ["What is covered?"]
        }
        response = client.post("/webhook/query", json=payload)
        assert response.status_code == 200
        assert "answers" in response.json()
    
    @pytest.mark.parametrize("age,expected", [
        (25, True),
        (15, False),
        (65, True)
    ])
    def test_age_validation(self, age, expected):
        """Test age validation logic."""
        result = validate_patient_age(age)
        assert result == expected
```

#### **Test Guidelines**

- **Test Naming**: Use descriptive test names that explain what is being tested
- **Arrange-Act-Assert**: Structure tests with clear sections
- **Edge Cases**: Test boundary conditions and error cases
- **Mocking**: Use mocks for external dependencies
- **Fixtures**: Use pytest fixtures for common setup

### **Test Coverage**

We aim for **90%+ test coverage**. Areas that must be covered:

- ✅ All API endpoints
- ✅ Business logic functions
- ✅ Error handling
- ✅ Data validation
- ✅ Webhook processing

## 🔄 **Pull Request Process**

### **1. Create a Feature Branch**

```bash
# Create and switch to new branch
git checkout -b feature/amazing-feature

# Or for bug fixes
git checkout -b fix/bug-description
```

### **2. Make Your Changes**

- Write clean, well-documented code
- Add tests for new functionality
- Update documentation if needed
- Follow the code style guidelines

### **3. Commit Your Changes**

```bash
# Stage your changes
git add .

# Commit with descriptive message
git commit -m "feat: add new insurance claim validation logic

- Add age-based validation rules
- Implement gender-specific scoring
- Add comprehensive test coverage
- Update API documentation

Closes #123"
```

#### **Commit Message Format**

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### **4. Push and Create Pull Request**

```bash
# Push to your fork
git push origin feature/amazing-feature
```

Then create a Pull Request on GitHub with:

#### **PR Template**
```markdown
## 📝 Description
Brief description of changes

## 🎯 Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Test addition

## 🧪 Testing
- [ ] Added unit tests
- [ ] Added integration tests
- [ ] All tests pass
- [ ] Manual testing completed

## 📋 Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Tests added/updated

## 🔗 Related Issues
Closes #123
```

### **5. Review Process**

1. **Automated Checks**: CI/CD pipeline runs tests and checks
2. **Code Review**: Maintainers review your code
3. **Address Feedback**: Make requested changes
4. **Merge**: Once approved, your PR will be merged

## 🐛 **Issue Reporting**

### **Before Reporting**

1. **Search Existing Issues**: Check if the issue is already reported
2. **Check Documentation**: Ensure the issue isn't covered in docs
3. **Reproduce**: Make sure you can consistently reproduce the issue

### **Issue Template**

```markdown
## 🐛 Bug Description
Clear and concise description of the bug

## 🔄 Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

## ✅ Expected Behavior
What you expected to happen

## ❌ Actual Behavior
What actually happened

## 📸 Screenshots
If applicable, add screenshots

## 💻 Environment
- OS: [e.g. macOS 12.0]
- Python: [e.g. 3.9.7]
- FastAPI: [e.g. 0.100.0]
- Browser: [e.g. Chrome 96]

## 📋 Additional Context
Any other context about the problem
```

## 📚 **Documentation**

### **Updating Documentation**

When adding new features, update:

1. **README.md**: Main project documentation
2. **API Documentation**: Endpoint descriptions and examples
3. **Code Comments**: Inline documentation
4. **Examples**: Usage examples and tutorials

### **Documentation Standards**

- Use clear, concise language
- Include code examples
- Add screenshots for UI changes
- Keep documentation up-to-date

## 🤝 **Code of Conduct**

### **Our Standards**

- **Be Respectful**: Treat everyone with respect
- **Be Inclusive**: Welcome contributors from all backgrounds
- **Be Constructive**: Provide helpful, constructive feedback
- **Be Professional**: Maintain professional behavior

### **Unacceptable Behavior**

- Harassment or discrimination
- Trolling or insulting comments
- Publishing private information
- Any conduct inappropriate in a professional setting

## 🏆 **Recognition**

Contributors will be recognized in:

- **README.md**: Contributors section
- **Release Notes**: Feature acknowledgments
- **GitHub**: Contributor statistics

## 📞 **Getting Help**

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: For private or sensitive matters

## 🎉 **Thank You**

Thank you for contributing to our project! Your contributions help make this project better for everyone.

---

**Happy Coding! 🚀**
