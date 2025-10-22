"""
Complaint Chatbot Package
LLM-based intelligent complaint collection system
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "Intelligent complaint collection chatbot with LLM"

from .chatbot_pipeline import ComplaintChatbot, ConversationalChatbot
from .config import Config

__all__ = [
    "ComplaintChatbot",
    "ConversationalChatbot",
    "Config",
]
