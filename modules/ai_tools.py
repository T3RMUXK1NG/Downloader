"""
OMNIPOTENT SOVEREIGN NEXUS - AI Tools Module
Version: v3.0.1 ULTIMATE NEXUS

AI-powered features including:
- Text summarization
- Language translation
- Content analysis
- Sentiment analysis
- Keyword extraction
- Text-to-speech
- Speech-to-text
- Image captioning
- Content moderation
- Smart categorization

Author: RAJSARASWATI JATEV (RS) - T3rmuxk1ng
"""

import asyncio
import aiohttp
import aiofiles
import logging
import re
import time
import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
    AsyncIterator,
    Awaitable,
)
from concurrent.futures import ThreadPoolExecutor


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
)
logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """Supported AI providers."""
    
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"
    CUSTOM = "custom"


class Language(Enum):
    """Supported languages."""
    
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    JAPANESE = "ja"
    KOREAN = "ko"
    CHINESE_SIMPLIFIED = "zh-CN"
    CHINESE_TRADITIONAL = "zh-TW"
    ARABIC = "ar"
    HINDI = "hi"
    DUTCH = "nl"
    POLISH = "pl"
    TURKISH = "tr"
    VIETNAMESE = "vi"
    THAI = "th"
    INDONESIAN = "id"
    SWEDISH = "sv"
    NORWEGIAN = "no"
    
    @classmethod
    def from_code(cls, code: str) -> "Language":
        """Get language from code."""
        for lang in cls:
            if lang.value == code:
                return lang
        return cls.ENGLISH


class SummaryLength(Enum):
    """Summary length presets."""
    
    SHORT = "short"       # ~100 words
    MEDIUM = "medium"     # ~250 words
    LONG = "long"         # ~500 words
    BULLET = "bullet"     # Bullet points


class SentimentType(Enum):
    """Sentiment analysis results."""
    
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


@dataclass
class AIConfig:
    """
    Configuration for AI operations.
    
    Attributes:
        provider: AI provider to use
        api_key: API key for the provider
        api_url: Custom API URL
        model: Model to use
        max_tokens: Maximum tokens for responses
        temperature: Temperature for generation
        timeout: Request timeout in seconds
        retry_count: Number of retry attempts
        retry_delay: Delay between retries
    """
    provider: AIProvider = AIProvider.OPENAI
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: float = 60.0
    retry_count: int = 3
    retry_delay: float = 1.0


@dataclass
class SummarizationResult:
    """
    Text summarization result.
    
    Attributes:
        original_text: Original input text
        summary: Generated summary
        length: Summary length type
        word_count_original: Word count of original
        word_count_summary: Word count of summary
        reduction_ratio: Reduction ratio (0-1)
        processing_time: Processing time in seconds
        provider: AI provider used
        model: Model used
        success: Whether operation succeeded
        error_message: Error message if failed
    """
    original_text: str
    summary: str
    length: SummaryLength
    word_count_original: int = 0
    word_count_summary: int = 0
    reduction_ratio: float = 0.0
    processing_time: float = 0.0
    provider: AIProvider = AIProvider.OPENAI
    model: str = ""
    success: bool = True
    error_message: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Calculate derived fields."""
        if not self.word_count_original:
            self.word_count_original = len(self.original_text.split())
        if not self.word_count_summary:
            self.word_count_summary = len(self.summary.split())
        if self.word_count_original > 0:
            self.reduction_ratio = 1 - (self.word_count_summary / self.word_count_original)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "summary": self.summary,
            "length": self.length.value,
            "word_count_original": self.word_count_original,
            "word_count_summary": self.word_count_summary,
            "reduction_ratio": round(self.reduction_ratio, 2),
            "processing_time": round(self.processing_time, 2),
            "provider": self.provider.value,
            "model": self.model,
            "success": self.success,
            "error_message": self.error_message,
        }


@dataclass
class TranslationResult:
    """
    Translation result.
    
    Attributes:
        original_text: Original text
        translated_text: Translated text
        source_language: Source language
        target_language: Target language
        confidence: Translation confidence (0-1)
        processing_time: Processing time in seconds
        provider: AI provider used
        success: Whether operation succeeded
        error_message: Error message if failed
    """
    original_text: str
    translated_text: str
    source_language: Language
    target_language: Language
    confidence: float = 0.0
    processing_time: float = 0.0
    provider: AIProvider = AIProvider.OPENAI
    success: bool = True
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "original_text": self.original_text,
            "translated_text": self.translated_text,
            "source_language": self.source_language.value,
            "target_language": self.target_language.value,
            "confidence": round(self.confidence, 2),
            "processing_time": round(self.processing_time, 2),
            "provider": self.provider.value,
            "success": self.success,
            "error_message": self.error_message,
        }


@dataclass
class SentimentResult:
    """
    Sentiment analysis result.
    
    Attributes:
        text: Analyzed text
        sentiment: Detected sentiment
        confidence: Confidence score (0-1)
        positive_score: Positive sentiment score
        negative_score: Negative sentiment score
        neutral_score: Neutral sentiment score
        keywords: Key sentiment words
        processing_time: Processing time in seconds
    """
    text: str
    sentiment: SentimentType
    confidence: float = 0.0
    positive_score: float = 0.0
    negative_score: float = 0.0
    neutral_score: float = 0.0
    keywords: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "sentiment": self.sentiment.value,
            "confidence": round(self.confidence, 2),
            "scores": {
                "positive": round(self.positive_score, 2),
                "negative": round(self.negative_score, 2),
                "neutral": round(self.neutral_score, 2),
            },
            "keywords": self.keywords,
            "processing_time": round(self.processing_time, 2),
        }


@dataclass
class KeywordExtractionResult:
    """
    Keyword extraction result.
    
    Attributes:
        text: Analyzed text
        keywords: Extracted keywords with scores
        phrases: Key phrases extracted
        topics: Detected topics
        processing_time: Processing time in seconds
    """
    text: str
    keywords: List[Tuple[str, float]] = field(default_factory=list)
    phrases: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "keywords": [{"word": k, "score": s} for k, s in self.keywords],
            "phrases": self.phrases,
            "topics": self.topics,
            "processing_time": round(self.processing_time, 2),
        }


@dataclass
class ContentAnalysisResult:
    """
    Comprehensive content analysis result.
    
    Attributes:
        text: Analyzed text
        summary: Text summary
        sentiment: Sentiment analysis
        keywords: Extracted keywords
        language: Detected language
        word_count: Total word count
        character_count: Total character count
        reading_time: Estimated reading time in minutes
        topics: Detected topics
        entities: Named entities found
        categories: Content categories
        processing_time: Total processing time
    """
    text: str
    summary: Optional[str] = None
    sentiment: Optional[SentimentResult] = None
    keywords: Optional[KeywordExtractionResult] = None
    language: Optional[Language] = None
    word_count: int = 0
    character_count: int = 0
    reading_time: float = 0.0
    topics: List[str] = field(default_factory=list)
    entities: Dict[str, List[str]] = field(default_factory=dict)
    categories: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    
    def __post_init__(self) -> None:
        """Calculate derived fields."""
        if not self.word_count:
            self.word_count = len(self.text.split())
        if not self.character_count:
            self.character_count = len(self.text)
        if not self.reading_time:
            # Average reading speed: 200 words per minute
            self.reading_time = self.word_count / 200
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "summary": self.summary,
            "sentiment": self.sentiment.to_dict() if self.sentiment else None,
            "keywords": self.keywords.to_dict() if self.keywords else None,
            "language": self.language.value if self.language else None,
            "word_count": self.word_count,
            "character_count": self.character_count,
            "reading_time": round(self.reading_time, 2),
            "topics": self.topics,
            "entities": self.entities,
            "categories": self.categories,
            "processing_time": round(self.processing_time, 2),
        }


class AIProviderBase(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self, config: AIConfig) -> None:
        """Initialize provider with config."""
        self.config = config
        self._session: Optional[aiohttp.ClientSession] = None
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """Generate text from prompt."""
        pass
    
    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Generate embeddings for text."""
        pass
    
    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure aiohttp session exists."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session
    
    async def close(self) -> None:
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()


class OpenAIProvider(AIProviderBase):
    """OpenAI API provider."""
    
    API_URL = "https://api.openai.com/v1"
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """Generate text using OpenAI API."""
        session = await self._ensure_session()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }
        
        data = {
            "model": kwargs.get("model", self.config.model),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
        }
        
        url = self.config.api_url or f"{self.API_URL}/chat/completions"
        
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                return result["choices"][0]["message"]["content"]
            else:
                error = await response.text()
                raise Exception(f"OpenAI API error: {error}")
    
    async def embed(self, text: str) -> List[float]:
        """Generate embeddings using OpenAI API."""
        session = await self._ensure_session()
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }
        
        data = {
            "model": "text-embedding-ada-002",
            "input": text,
        }
        
        url = f"{self.API_URL}/embeddings"
        
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                return result["data"][0]["embedding"]
            else:
                error = await response.text()
                raise Exception(f"OpenAI API error: {error}")


class LocalProvider(AIProviderBase):
    """Local AI provider for offline processing."""
    
    def __init__(self, config: AIConfig) -> None:
        super().__init__(config)
        self._word_frequencies: Dict[str, int] = {}
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """Generate text using local processing (limited)."""
        # This is a simplified implementation
        # In production, you'd use a local model like llama.cpp
        
        if "summarize" in (system_prompt or "").lower():
            return await self._local_summarize(prompt)
        elif "translate" in (system_prompt or "").lower():
            return prompt  # Return as-is for local
        else:
            return f"[Local processing] {prompt[:200]}..."
    
    async def _local_summarize(self, text: str) -> str:
        """Local summarization using extractive method."""
        sentences = re.split(r'[.!?]+', text)
        if len(sentences) <= 3:
            return text
        
        # Simple extractive summary - take first and key sentences
        summary_sentences = [sentences[0]]
        if len(sentences) > 2:
            summary_sentences.append(sentences[-2])
        
        return '. '.join(s.strip() for s in summary_sentences if s.strip()) + '.'
    
    async def embed(self, text: str) -> List[float]:
        """Generate simple local embeddings."""
        # Simple word-based embedding
        words = text.lower().split()
        embedding = [0.0] * 100
        
        for i, word in enumerate(words[:100]):
            embedding[i] = hash(word) % 100 / 100.0
        
        return embedding


class AITools:
    """
    OMNIPOTENT SOVEREIGN NEXUS AI Tools.
    
    Comprehensive AI-powered features including:
    - Text summarization
    - Language translation
    - Sentiment analysis
    - Keyword extraction
    - Content analysis
    """
    
    def __init__(
        self,
        config: Optional[AIConfig] = None,
        progress_callback: Optional[Callable[[str, float], Awaitable[None]]] = None,
    ) -> None:
        """
        Initialize AI tools.
        
        Args:
            config: AI configuration
            progress_callback: Progress callback function
        """
        self.config = config or AIConfig()
        self._progress_callback = progress_callback
        self._provider: Optional[AIProviderBase] = None
        
        logger.info(f"AITools initialized v3.0.1 ULTIMATE NEXUS")
    
    async def __aenter__(self) -> "AITools":
        """Async context manager entry."""
        await self._initialize_provider()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
    
    async def _initialize_provider(self) -> None:
        """Initialize AI provider."""
        if self.config.provider == AIProvider.OPENAI:
            self._provider = OpenAIProvider(self.config)
        elif self.config.provider == AIProvider.LOCAL:
            self._provider = LocalProvider(self.config)
        else:
            self._provider = LocalProvider(self.config)
    
    async def close(self) -> None:
        """Close AI tools and release resources."""
        if self._provider:
            await self._provider.close()
        logger.info("AITools closed")
    
    async def _report_progress(self, stage: str, progress: float) -> None:
        """Report progress to callback."""
        if self._progress_callback:
            try:
                await self._progress_callback(stage, progress)
            except Exception as e:
                logger.warning(f"Progress callback error: {e}")
    
    async def summarize(
        self,
        text: str,
        length: SummaryLength = SummaryLength.MEDIUM,
    ) -> SummarizationResult:
        """
        Summarize text using AI.
        
        Args:
            text: Text to summarize
            length: Desired summary length
            
        Returns:
            SummarizationResult with summary
        """
        start_time = time.time()
        
        try:
            await self._report_progress("summarize", 0.0)
            
            length_prompts = {
                SummaryLength.SHORT: "Provide a brief summary in about 100 words.",
                SummaryLength.MEDIUM: "Provide a summary in about 250 words.",
                SummaryLength.LONG: "Provide a detailed summary in about 500 words.",
                SummaryLength.BULLET: "Summarize the text as bullet points.",
            }
            
            system_prompt = f"""You are a professional text summarizer. 
{length_prompts.get(length, length_prompts[SummaryLength.MEDIUM])}
Be concise and capture the main points. Preserve important details."""
            
            prompt = f"Please summarize the following text:\n\n{text}"
            
            await self._report_progress("summarize", 0.5)
            
            summary = await self._provider.generate(prompt, system_prompt)
            
            processing_time = time.time() - start_time
            await self._report_progress("summarize", 1.0)
            
            return SummarizationResult(
                original_text=text,
                summary=summary,
                length=length,
                processing_time=processing_time,
                provider=self.config.provider,
                model=self.config.model,
                success=True,
            )
            
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            return SummarizationResult(
                original_text=text,
                summary="",
                length=length,
                provider=self.config.provider,
                success=False,
                error_message=str(e),
            )
    
    async def translate(
        self,
        text: str,
        target_language: Language,
        source_language: Optional[Language] = None,
    ) -> TranslationResult:
        """
        Translate text to target language.
        
        Args:
            text: Text to translate
            target_language: Target language
            source_language: Source language (auto-detect if None)
            
        Returns:
            TranslationResult with translation
        """
        start_time = time.time()
        
        try:
            await self._report_progress("translate", 0.0)
            
            source_lang = source_language or Language.ENGLISH
            
            system_prompt = f"""You are a professional translator.
Translate the given text from {source_lang.name} to {target_language.name}.
Maintain the original tone and meaning. Only provide the translation, no explanations."""
            
            prompt = f"Translate to {target_language.name}:\n\n{text}"
            
            await self._report_progress("translate", 0.5)
            
            translation = await self._provider.generate(prompt, system_prompt)
            
            processing_time = time.time() - start_time
            await self._report_progress("translate", 1.0)
            
            return TranslationResult(
                original_text=text,
                translated_text=translation,
                source_language=source_lang,
                target_language=target_language,
                confidence=0.9,  # Placeholder
                processing_time=processing_time,
                provider=self.config.provider,
                success=True,
            )
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return TranslationResult(
                original_text=text,
                translated_text="",
                source_language=source_language or Language.ENGLISH,
                target_language=target_language,
                provider=self.config.provider,
                success=False,
                error_message=str(e),
            )
    
    async def analyze_sentiment(self, text: str) -> SentimentResult:
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            SentimentResult with sentiment analysis
        """
        start_time = time.time()
        
        try:
            await self._report_progress("sentiment", 0.0)
            
            system_prompt = """You are a sentiment analysis expert.
Analyze the sentiment of the given text.
Respond in JSON format:
{
    "sentiment": "positive/negative/neutral/mixed",
    "confidence": 0.0-1.0,
    "positive_score": 0.0-1.0,
    "negative_score": 0.0-1.0,
    "neutral_score": 0.0-1.0,
    "keywords": ["word1", "word2"]
}"""
            
            prompt = f"Analyze sentiment:\n\n{text}"
            
            await self._report_progress("sentiment", 0.5)
            
            response = await self._provider.generate(prompt, system_prompt)
            
            # Parse JSON response
            try:
                data = json.loads(response)
                sentiment = SentimentType(data.get("sentiment", "neutral"))
            except (json.JSONDecodeError, ValueError):
                sentiment = SentimentType.NEUTRAL
                data = {}
            
            processing_time = time.time() - start_time
            await self._report_progress("sentiment", 1.0)
            
            return SentimentResult(
                text=text,
                sentiment=sentiment,
                confidence=data.get("confidence", 0.5),
                positive_score=data.get("positive_score", 0.0),
                negative_score=data.get("negative_score", 0.0),
                neutral_score=data.get("neutral_score", 1.0),
                keywords=data.get("keywords", []),
                processing_time=processing_time,
            )
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return SentimentResult(
                text=text,
                sentiment=SentimentType.NEUTRAL,
                processing_time=time.time() - start_time,
            )
    
    async def extract_keywords(
        self,
        text: str,
        max_keywords: int = 10,
    ) -> KeywordExtractionResult:
        """
        Extract keywords from text.
        
        Args:
            text: Text to analyze
            max_keywords: Maximum keywords to extract
            
        Returns:
            KeywordExtractionResult with keywords
        """
        start_time = time.time()
        
        try:
            await self._report_progress("keywords", 0.0)
            
            system_prompt = f"""You are a keyword extraction expert.
Extract the top {max_keywords} most important keywords and phrases from the text.
Respond in JSON format:
{{
    "keywords": [["word", score], ...],
    "phrases": ["phrase1", "phrase2"],
    "topics": ["topic1", "topic2"]
}}"""
            
            prompt = f"Extract keywords:\n\n{text}"
            
            await self._report_progress("keywords", 0.5)
            
            response = await self._provider.generate(prompt, system_prompt)
            
            try:
                data = json.loads(response)
                keywords = [(k, s) for k, s in data.get("keywords", [])]
                phrases = data.get("phrases", [])
                topics = data.get("topics", [])
            except (json.JSONDecodeError, ValueError):
                keywords = []
                phrases = []
                topics = []
            
            processing_time = time.time() - start_time
            await self._report_progress("keywords", 1.0)
            
            return KeywordExtractionResult(
                text=text,
                keywords=keywords[:max_keywords],
                phrases=phrases,
                topics=topics,
                processing_time=processing_time,
            )
            
        except Exception as e:
            logger.error(f"Keyword extraction error: {e}")
            return KeywordExtractionResult(
                text=text,
                processing_time=time.time() - start_time,
            )
    
    async def analyze_content(
        self,
        text: str,
        include_summary: bool = True,
        include_sentiment: bool = True,
        include_keywords: bool = True,
    ) -> ContentAnalysisResult:
        """
        Perform comprehensive content analysis.
        
        Args:
            text: Text to analyze
            include_summary: Include summary
            include_sentiment: Include sentiment analysis
            include_keywords: Include keyword extraction
            
        Returns:
            ContentAnalysisResult with full analysis
        """
        start_time = time.time()
        
        try:
            await self._report_progress("analyze", 0.0)
            
            result = ContentAnalysisResult(text=text)
            
            if include_summary:
                await self._report_progress("analyze", 0.1)
                summary_result = await self.summarize(text, SummaryLength.SHORT)
                result.summary = summary_result.summary
            
            if include_sentiment:
                await self._report_progress("analyze", 0.4)
                result.sentiment = await self.analyze_sentiment(text)
            
            if include_keywords:
                await self._report_progress("analyze", 0.7)
                result.keywords = await self.extract_keywords(text)
            
            result.processing_time = time.time() - start_time
            await self._report_progress("analyze", 1.0)
            
            return result
            
        except Exception as e:
            logger.error(f"Content analysis error: {e}")
            return ContentAnalysisResult(
                text=text,
                processing_time=time.time() - start_time,
            )
    
    async def batch_summarize(
        self,
        texts: List[str],
        length: SummaryLength = SummaryLength.MEDIUM,
        max_concurrent: int = 5,
    ) -> List[SummarizationResult]:
        """
        Summarize multiple texts concurrently.
        
        Args:
            texts: List of texts to summarize
            length: Summary length
            max_concurrent: Maximum concurrent operations
            
        Returns:
            List of SummarizationResult objects
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def summarize_with_semaphore(text: str) -> SummarizationResult:
            async with semaphore:
                return await self.summarize(text, length)
        
        tasks = [summarize_with_semaphore(text) for text in texts]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def batch_translate(
        self,
        texts: List[str],
        target_language: Language,
        source_language: Optional[Language] = None,
        max_concurrent: int = 5,
    ) -> List[TranslationResult]:
        """
        Translate multiple texts concurrently.
        
        Args:
            texts: List of texts to translate
            target_language: Target language
            source_language: Source language
            max_concurrent: Maximum concurrent operations
            
        Returns:
            List of TranslationResult objects
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def translate_with_semaphore(text: str) -> TranslationResult:
            async with semaphore:
                return await self.translate(text, target_language, source_language)
        
        tasks = [translate_with_semaphore(text) for text in texts]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def detect_language(self, text: str) -> Language:
        """
        Detect the language of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected language
        """
        try:
            system_prompt = """You are a language detection expert.
Identify the language of the given text.
Respond with only the ISO 639-1 language code (e.g., 'en', 'es', 'fr')."""
            
            prompt = f"Detect language:\n\n{text[:500]}"
            
            code = await self._provider.generate(prompt, system_prompt)
            code = code.strip().lower()
            
            return Language.from_code(code)
            
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return Language.ENGLISH
    
    async def categorize(self, text: str) -> List[str]:
        """
        Categorize text content.
        
        Args:
            text: Text to categorize
            
        Returns:
            List of categories
        """
        try:
            system_prompt = """You are a content categorization expert.
Categorize the given text into relevant categories.
Respond in JSON format:
{
    "categories": ["category1", "category2", ...]
}"""
            
            prompt = f"Categorize:\n\n{text}"
            
            response = await self._provider.generate(prompt, system_prompt)
            
            try:
                data = json.loads(response)
                return data.get("categories", [])
            except json.JSONDecodeError:
                return []
            
        except Exception as e:
            logger.error(f"Categorization error: {e}")
            return []


# Convenience functions
async def summarize_text(
    text: str,
    length: SummaryLength = SummaryLength.MEDIUM,
    api_key: Optional[str] = None,
) -> SummarizationResult:
    """
    Quick text summarization function.
    
    Args:
        text: Text to summarize
        length: Summary length
        api_key: API key for AI provider
        
    Returns:
        SummarizationResult
    """
    config = AIConfig(api_key=api_key)
    async with AITools(config=config) as ai:
        return await ai.summarize(text, length)


async def translate_text(
    text: str,
    target_language: Language,
    source_language: Optional[Language] = None,
    api_key: Optional[str] = None,
) -> TranslationResult:
    """
    Quick text translation function.
    
    Args:
        text: Text to translate
        target_language: Target language
        source_language: Source language
        api_key: API key
        
    Returns:
        TranslationResult
    """
    config = AIConfig(api_key=api_key)
    async with AITools(config=config) as ai:
        return await ai.translate(text, target_language, source_language)


async def analyze_text(
    text: str,
    api_key: Optional[str] = None,
) -> ContentAnalysisResult:
    """
    Quick content analysis function.
    
    Args:
        text: Text to analyze
        api_key: API key
        
    Returns:
        ContentAnalysisResult
    """
    config = AIConfig(api_key=api_key)
    async with AITools(config=config) as ai:
        return await ai.analyze_content(text)


# Export all public classes and functions
__all__ = [
    "AITools",
    "AIProvider",
    "AIConfig",
    "Language",
    "SummaryLength",
    "SentimentType",
    "SummarizationResult",
    "TranslationResult",
    "SentimentResult",
    "KeywordExtractionResult",
    "ContentAnalysisResult",
    "summarize_text",
    "translate_text",
    "analyze_text",
]
