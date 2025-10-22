"""
Veri modelleri ve şemaları
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class CategoryField:
    """Kategori alanı modeli"""
    field_name: str  # alan adı (örn: atm_lokasyonu)
    question: str    # sorulacak soru
    field_type: str = "string"  # alan tipi
    required: bool = True

@dataclass
class Category:
    """Kategori modeli"""
    category_name: str
    fields: List[CategoryField]
    description: Optional[str] = None

@dataclass
class ExtractedData:
    """LLM'den çıkarılan veri"""
    category: str
    fields: Dict[str, Any]  # {field_name: value or None}
    confidence: float = 0.0

@dataclass
class ConversationState:
    """Sohbet durumu"""
    original_complaint: str
    category: Optional[str] = None
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    pending_questions: List[CategoryField] = field(default_factory=list)
    current_question_index: int = 0
    is_complete: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_current_question(self) -> Optional[CategoryField]:
        """Şu anki soruyu döndür"""
        if self.current_question_index < len(self.pending_questions):
            return self.pending_questions[self.current_question_index]
        return None
    
    def move_to_next_question(self):
        """Sonraki soruya geç"""
        self.current_question_index += 1
        if self.current_question_index >= len(self.pending_questions):
            self.is_complete = True

@dataclass
class ChatMessage:
    """Chat mesajı"""
    role: str  # "user" veya "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
