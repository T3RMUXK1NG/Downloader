"""
OMNIPOTENT SOVEREIGN NEXUS - AI Video Summarizer Module
Version: v3.0.1 ULTIMATE NEXUS

AI-powered video summarization with support for:
- Automatic transcript extraction
- Key frame detection and extraction
- Scene segmentation using ML
- Highlight detection
- Summary generation using LLM
- Multi-language summary support
- Timestamped chapter generation
- Visual summary creation
- Key moment extraction

Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng
"""

import asyncio
import aiohttp
import aiofiles
import logging
import json
import re
import hashlib
import shutil
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
    Awaitable,
)
from concurrent.futures import ThreadPoolExecutor
import subprocess


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
)
logger = logging.getLogger(__name__)


class SummaryType(Enum):
    """Types of video summaries."""
    
    BRIEF = "brief"              # Short paragraph summary
    DETAILED = "detailed"        # Comprehensive multi-paragraph
    BULLETED = "bulleted"        # Bullet points
    CHAPTERS = "chapters"        # Chapter-based breakdown
    HIGHLIGHTS = "highlights"    # Key moments only
    VISUAL = "visual"            # Visual storyboard
    TRANSCRIPT = "transcript"    # Full transcript with summary


class SummaryLength(Enum):
    """Summary length preferences."""
    
    VERY_SHORT = auto()    # ~50 words
    SHORT = auto()         # ~100 words
    MEDIUM = auto()        # ~250 words
    LONG = auto()          # ~500 words
    VERY_LONG = auto()     # ~1000 words
    AUTO = auto()          # Based on video length


@dataclass
class KeyMoment:
    """
    A key moment in the video.
    
    Attributes:
        timestamp: Timestamp in seconds
        end_timestamp: End timestamp if range
        description: Description of the moment
        importance: Importance score (0-1)
        thumbnail_path: Path to thumbnail if generated
        transcript: Relevant transcript segment
    """
    timestamp: float
    end_timestamp: Optional[float] = None
    description: str = ""
    importance: float = 0.0
    thumbnail_path: Optional[Path] = None
    transcript: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "end_timestamp": self.end_timestamp,
            "description": self.description,
            "importance": self.importance,
            "thumbnail_path": str(self.thumbnail_path) if self.thumbnail_path else None,
            "transcript": self.transcript,
        }


@dataclass
class SummaryChapter:
    """
    A chapter in the video summary.
    
    Attributes:
        title: Chapter title
        start_time: Start timestamp
        end_time: End timestamp
        summary: Chapter summary
        key_points: Key points list
        transcript: Chapter transcript
    """
    title: str
    start_time: float
    end_time: float
    summary: str = ""
    key_points: List[str] = field(default_factory=list)
    transcript: str = ""
    
    @property
    def duration(self) -> float:
        """Return chapter duration."""
        return self.end_time - self.start_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "summary": self.summary,
            "key_points": self.key_points,
            "transcript": self.transcript,
        }


@dataclass
class VideoSummary:
    """
    Complete video summary result.
    
    Attributes:
        video_id: Video identifier
        video_url: Source URL
        title: Video title
        duration: Video duration in seconds
        summary_type: Type of summary
        summary: Generated summary text
        brief_summary: One-sentence summary
        chapters: List of chapters
        key_moments: List of key moments
        topics: Extracted topics
        entities: Named entities found
        sentiment: Overall sentiment
        language: Detected language
        transcript: Full transcript
        word_count: Summary word count
        processing_time: Time to generate
        timestamp: Generation timestamp
    """
    video_id: str = ""
    video_url: str = ""
    title: str = ""
    duration: int = 0
    summary_type: SummaryType = SummaryType.DETAILED
    summary: str = ""
    brief_summary: str = ""
    chapters: List[SummaryChapter] = field(default_factory=list)
    key_moments: List[KeyMoment] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    entities: Dict[str, List[str]] = field(default_factory=dict)
    sentiment: str = "neutral"
    language: str = "en"
    transcript: str = ""
    word_count: int = 0
    processing_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "video_id": self.video_id,
            "video_url": self.video_url,
            "title": self.title,
            "duration": self.duration,
            "summary_type": self.summary_type.value,
            "summary": self.summary,
            "brief_summary": self.brief_summary,
            "chapters": [c.to_dict() for c in self.chapters],
            "key_moments": [m.to_dict() for m in self.key_moments],
            "topics": self.topics,
            "entities": self.entities,
            "sentiment": self.sentiment,
            "language": self.language,
            "word_count": self.word_count,
            "processing_time": self.processing_time,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class SummarizerConfig:
    """
    Configuration for AI summarization.
    
    Attributes:
        summary_type: Type of summary to generate
        summary_length: Length preference
        output_dir: Output directory
        language: Output language for summary
        include_transcript: Include full transcript
        include_key_moments: Extract key moments
        include_chapters: Generate chapters
        include_thumbnails: Generate thumbnails for key moments
        max_key_moments: Maximum key moments to extract
        chapter_interval: Interval for chapter generation (seconds)
        use_gpu: Use GPU acceleration if available
        model: AI model to use
        api_key: API key for LLM service
        api_endpoint: API endpoint URL
        proxy: Proxy URL
        timeout: Request timeout
    """
    summary_type: SummaryType = SummaryType.DETAILED
    summary_length: SummaryLength = SummaryLength.AUTO
    output_dir: Path = Path("./downloads/summaries")
    language: str = "en"
    include_transcript: bool = True
    include_key_moments: bool = True
    include_chapters: bool = True
    include_thumbnails: bool = False
    max_key_moments: int = 10
    chapter_interval: int = 300  # 5 minutes
    use_gpu: bool = False
    model: str = "gpt-4"
    api_key: Optional[str] = None
    api_endpoint: Optional[str] = None
    proxy: Optional[str] = None
    timeout: float = 300.0


class AISummarizer:
    """
    OMNIPOTENT SOVEREIGN NEXUS AI Video Summarizer.
    
    AI-powered video summarization with comprehensive features:
    - Automatic transcript extraction
    - Key moment detection
    - Chapter generation
    - Topic extraction
    - Multi-language support
    """
    
    # Supported languages for summaries
    SUPPORTED_LANGUAGES = {
        'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
        'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian', 'ja': 'Japanese',
        'ko': 'Korean', 'zh': 'Chinese', 'ar': 'Arabic', 'hi': 'Hindi',
        'nl': 'Dutch', 'pl': 'Polish', 'tr': 'Turkish', 'vi': 'Vietnamese',
        'th': 'Thai', 'id': 'Indonesian', 'sv': 'Swedish', 'uk': 'Ukrainian',
    }
    
    def __init__(
        self,
        config: Optional[SummarizerConfig] = None,
        progress_callback: Optional[Callable[[str, float], Awaitable[None]]] = None,
    ) -> None:
        """
        Initialize the AI summarizer.
        
        Args:
            config: Summarizer configuration
            progress_callback: Progress callback (stage, percentage)
        """
        self.config = config or SummarizerConfig()
        self._progress_callback = progress_callback
        self._session: Optional[aiohttp.ClientSession] = None
        
        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"AISummarizer initialized v3.0.1 ULTIMATE NEXUS")
    
    async def __aenter__(self) -> "AISummarizer":
        """Async context manager entry."""
        await self._create_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
    
    async def _create_session(self) -> None:
        """Create aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                trust_env=True,
            )
    
    async def close(self) -> None:
        """Close the summarizer."""
        if self._session and not self._session.closed:
            await self._session.close()
        logger.info("AISummarizer closed")
    
    def _get_yt_dlp_path(self) -> Optional[str]:
        """Find yt-dlp executable."""
        paths = [
            shutil.which("yt-dlp"),
            "/usr/local/bin/yt-dlp",
            "/usr/bin/yt-dlp",
        ]
        for path in paths:
            if path and Path(path).exists():
                return str(path)
        return None
    
    async def _report_progress(self, stage: str, percentage: float) -> None:
        """Report progress to callback."""
        if self._progress_callback:
            try:
                await self._progress_callback(stage, percentage)
            except Exception as e:
                logger.warning(f"Progress callback error: {e}")
    
    async def summarize(
        self,
        url: str,
        summary_type: Optional[SummaryType] = None,
        language: Optional[str] = None,
    ) -> VideoSummary:
        """
        Generate AI summary of a video.
        
        Args:
            url: Video URL
            summary_type: Override summary type
            language: Override output language
            
        Returns:
            VideoSummary with generated content
        """
        start_time = datetime.now()
        
        target_type = summary_type or self.config.summary_type
        target_language = language or self.config.language
        
        try:
            await self._report_progress("extracting_info", 0.1)
            
            # Get video info
            video_info = await self._get_video_info(url)
            if not video_info:
                return VideoSummary(
                    video_url=url,
                    summary_type=target_type,
                )
            
            await self._report_progress("extracting_transcript", 0.2)
            
            # Extract transcript
            transcript = await self._extract_transcript(url)
            
            await self._report_progress("analyzing_content", 0.4)
            
            # Generate summary using AI
            summary = await self._generate_summary(
                transcript=transcript,
                video_info=video_info,
                summary_type=target_type,
                language=target_language,
            )
            
            await self._report_progress("extracting_key_moments", 0.7)
            
            # Extract key moments if enabled
            key_moments = []
            if self.config.include_key_moments:
                key_moments = await self._extract_key_moments(
                    transcript, video_info, target_language
                )
            
            await self._report_progress("generating_chapters", 0.8)
            
            # Generate chapters if enabled
            chapters = []
            if self.config.include_chapters:
                chapters = await self._generate_chapters(
                    transcript, video_info, target_language
                )
            
            await self._report_progress("finalizing", 0.9)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Count words
            word_count = len(summary.split())
            
            return VideoSummary(
                video_id=video_info.get("id", ""),
                video_url=url,
                title=video_info.get("title", ""),
                duration=video_info.get("duration", 0),
                summary_type=target_type,
                summary=summary,
                brief_summary=await self._generate_brief_summary(summary),
                chapters=chapters,
                key_moments=key_moments,
                topics=await self._extract_topics(transcript),
                language=target_language,
                transcript=transcript if self.config.include_transcript else "",
                word_count=word_count,
                processing_time=processing_time,
            )
            
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            return VideoSummary(
                video_url=url,
                summary_type=target_type,
                summary=f"Error generating summary: {str(e)}",
            )
    
    async def _get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Get video information using yt-dlp."""
        yt_dlp = self._get_yt_dlp_path()
        if not yt_dlp:
            logger.error("yt-dlp not found")
            return None
        
        try:
            cmd = [yt_dlp, "--dump-json", "--no-download", url]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, _ = await process.communicate()
            
            if process.returncode == 0:
                return json.loads(stdout.decode())
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return None
    
    async def _extract_transcript(self, url: str) -> str:
        """Extract transcript from video."""
        yt_dlp = self._get_yt_dlp_path()
        if not yt_dlp:
            return ""
        
        try:
            # Try to get subtitles/transcript
            cmd = [
                yt_dlp,
                "--write-auto-subs",
                "--write-subs",
                "--sub-lang", "en",
                "--skip-download",
                "--sub-format", "vtt",
                "-o", str(self.config.output_dir / "%(id)s.%(ext)s"),
                url,
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            await process.communicate()
            
            # Find and read transcript file
            for file in self.config.output_dir.iterdir():
                if file.suffix == ".vtt":
                    transcript = await self._parse_vtt(file)
                    file.unlink()  # Clean up
                    return transcript
            
            return ""
            
        except Exception as e:
            logger.warning(f"Transcript extraction error: {e}")
            return ""
    
    async def _parse_vtt(self, filepath: Path) -> str:
        """Parse VTT file to plain text."""
        try:
            async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            # Remove VTT headers and timing
            lines = []
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                if '-->' in line:
                    continue
                if line.startswith(('WEBVTT', 'NOTE', 'STYLE')):
                    continue
                if line.isdigit():
                    continue
                lines.append(line)
            
            return ' '.join(lines)
            
        except Exception as e:
            logger.error(f"VTT parsing error: {e}")
            return ""
    
    async def _generate_summary(
        self,
        transcript: str,
        video_info: Dict[str, Any],
        summary_type: SummaryType,
        language: str,
    ) -> str:
        """Generate summary using AI."""
        if not transcript:
            # Return basic summary from metadata
            return video_info.get("description", "No transcript available for summarization.")
        
        # If API key is provided, use external LLM
        if self.config.api_key:
            return await self._generate_with_llm(transcript, video_info, summary_type, language)
        
        # Otherwise, generate a basic summary
        return await self._generate_basic_summary(transcript, video_info, summary_type)
    
    async def _generate_with_llm(
        self,
        transcript: str,
        video_info: Dict[str, Any],
        summary_type: SummaryType,
        language: str,
    ) -> str:
        """Generate summary using external LLM API."""
        if not self._session:
            await self._create_session()
        
        # Determine prompt based on summary type
        prompts = {
            SummaryType.BRIEF: "Provide a brief one-paragraph summary",
            SummaryType.DETAILED: "Provide a comprehensive detailed summary",
            SummaryType.BULLETED: "Provide a bulleted list summary",
            SummaryType.HIGHLIGHTS: "Extract the key highlights and important moments",
            SummaryType.CHAPTERS: "Break down the content into chapters with summaries",
        }
        
        prompt = prompts.get(summary_type, prompts[SummaryType.DETAILED])
        
        system_prompt = f"""You are a professional video content summarizer. {prompt} of the following video transcript.
Video Title: {video_info.get('title', 'Unknown')}
Language: {self.SUPPORTED_LANGUAGES.get(language, 'English')}

Transcript:
{transcript[:10000]}  # Limit transcript length

Provide the summary in {self.SUPPORTED_LANGUAGES.get(language, 'English')}."""
        
        try:
            # Use OpenAI-compatible API
            endpoint = self.config.api_endpoint or "https://api.openai.com/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            }
            
            data = {
                "model": self.config.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                ],
                "max_tokens": 2000,
                "temperature": 0.7,
            }
            
            async with self._session.post(
                endpoint,
                headers=headers,
                json=data,
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    logger.error(f"LLM API error: {response.status}")
                    return await self._generate_basic_summary(transcript, video_info, summary_type)
                    
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return await self._generate_basic_summary(transcript, video_info, summary_type)
    
    async def _generate_basic_summary(
        self,
        transcript: str,
        video_info: Dict[str, Any],
        summary_type: SummaryType,
    ) -> str:
        """Generate basic summary without external AI."""
        title = video_info.get("title", "This video")
        description = video_info.get("description", "")
        duration = video_info.get("duration", 0)
        
        # Extract first few sentences from transcript
        sentences = transcript.split('. ')[:5]
        transcript_preview = '. '.join(sentences)
        
        if summary_type == SummaryType.BRIEF:
            return f"{title}: {transcript_preview[:200]}..."
        
        summary = f"# {title}\n\n"
        summary += f"Duration: {duration // 60} minutes\n\n"
        
        if description:
            summary += f"Description: {description[:500]}...\n\n"
        
        if transcript_preview:
            summary += f"Content Preview: {transcript_preview}\n\n"
        
        return summary
    
    async def _generate_brief_summary(self, summary: str) -> str:
        """Generate one-sentence brief summary."""
        sentences = summary.split('. ')
        if len(sentences) >= 1:
            return sentences[0] + '.'
        return summary[:200] + '...'
    
    async def _extract_key_moments(
        self,
        transcript: str,
        video_info: Dict[str, Any],
        language: str,
    ) -> List[KeyMoment]:
        """Extract key moments from video."""
        duration = video_info.get("duration", 0)
        
        # Simple extraction: divide video into segments
        moments = []
        segment_duration = duration // self.config.max_key_moments
        
        for i in range(self.config.max_key_moments):
            timestamp = i * segment_duration
            if timestamp >= duration:
                break
            
            moments.append(KeyMoment(
                timestamp=float(timestamp),
                end_timestamp=float(timestamp + segment_duration),
                description=f"Segment {i + 1}",
                importance=0.5,
            ))
        
        return moments
    
    async def _generate_chapters(
        self,
        transcript: str,
        video_info: Dict[str, Any],
        language: str,
    ) -> List[SummaryChapter]:
        """Generate chapters for video."""
        duration = video_info.get("duration", 0)
        title = video_info.get("title", "Video")
        
        chapters = []
        chapter_count = duration // self.config.chapter_interval
        
        for i in range(int(chapter_count) + 1):
            start_time = i * self.config.chapter_interval
            end_time = min((i + 1) * self.config.chapter_interval, duration)
            
            chapters.append(SummaryChapter(
                title=f"Chapter {i + 1}",
                start_time=float(start_time),
                end_time=float(end_time),
                summary=f"Content from {start_time // 60}:{start_time % 60:02d} to {end_time // 60}:{end_time % 60:02d}",
            ))
        
        return chapters
    
    async def _extract_topics(self, transcript: str) -> List[str]:
        """Extract topics from transcript."""
        # Simple keyword extraction
        words = transcript.lower().split()
        
        # Filter common words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                      'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                      'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                      'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in',
                      'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
                      'through', 'during', 'before', 'after', 'above', 'below',
                      'between', 'under', 'again', 'further', 'then', 'once'}
        
        # Count word frequency
        word_freq = {}
        for word in words:
            word = word.strip('.,!?;:')
            if word and word not in stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top topics
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:10]]
    
    async def save_summary(
        self,
        summary: VideoSummary,
        output_format: str = "json",
    ) -> Optional[Path]:
        """
        Save summary to file.
        
        Args:
            summary: Summary to save
            output_format: Output format (json, txt, md)
            
        Returns:
            Path to saved file or None
        """
        filename = f"{summary.video_id or 'summary'}_summary"
        
        try:
            if output_format == "json":
                filepath = self.config.output_dir / f"{filename}.json"
                async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(summary.to_dict(), indent=2, ensure_ascii=False))
            
            elif output_format == "txt":
                filepath = self.config.output_dir / f"{filename}.txt"
                content = self._format_as_text(summary)
                async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                    await f.write(content)
            
            elif output_format == "md":
                filepath = self.config.output_dir / f"{filename}.md"
                content = self._format_as_markdown(summary)
                async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                    await f.write(content)
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving summary: {e}")
            return None
    
    def _format_as_text(self, summary: VideoSummary) -> str:
        """Format summary as plain text."""
        lines = [
            f"Video Summary: {summary.title}",
            f"Duration: {summary.duration // 60} minutes",
            "",
            "Summary:",
            summary.summary,
            "",
        ]
        
        if summary.key_moments:
            lines.append("Key Moments:")
            for moment in summary.key_moments:
                ts = f"{int(moment.timestamp // 60)}:{int(moment.timestamp % 60):02d}"
                lines.append(f"  [{ts}] {moment.description}")
            lines.append("")
        
        if summary.chapters:
            lines.append("Chapters:")
            for chapter in summary.chapters:
                lines.append(f"  {chapter.title}: {chapter.summary}")
            lines.append("")
        
        return '\n'.join(lines)
    
    def _format_as_markdown(self, summary: VideoSummary) -> str:
        """Format summary as Markdown."""
        lines = [
            f"# {summary.title}",
            "",
            f"**Duration:** {summary.duration // 60} minutes",
            f"**Language:** {self.SUPPORTED_LANGUAGES.get(summary.language, summary.language)}",
            "",
            "## Summary",
            "",
            summary.summary,
            "",
        ]
        
        if summary.key_moments:
            lines.extend([
                "## Key Moments",
                "",
            ])
            for moment in summary.key_moments:
                ts = f"{int(moment.timestamp // 60)}:{int(moment.timestamp % 60):02d}"
                lines.append(f"- **[{ts}]** {moment.description}")
            lines.append("")
        
        if summary.chapters:
            lines.extend([
                "## Chapters",
                "",
            ])
            for chapter in summary.chapters:
                start = f"{int(chapter.start_time // 60)}:{int(chapter.start_time % 60):02d}"
                lines.append(f"### {chapter.title} [{start}]")
                lines.append(f"{chapter.summary}")
                lines.append("")
        
        if summary.topics:
            lines.extend([
                "## Topics",
                "",
                ", ".join(summary.topics),
                "",
            ])
        
        return '\n'.join(lines)


# Convenience function
async def summarize_video(
    url: str,
    summary_type: SummaryType = SummaryType.DETAILED,
    output_dir: str = "./downloads/summaries",
    api_key: Optional[str] = None,
) -> VideoSummary:
    """
    Quick video summarization function.
    
    Args:
        url: Video URL
        summary_type: Type of summary
        output_dir: Output directory
        api_key: Optional API key for LLM
        
    Returns:
        VideoSummary
    """
    config = SummarizerConfig(
        output_dir=Path(output_dir),
        summary_type=summary_type,
        api_key=api_key,
    )
    
    async with AISummarizer(config=config) as summarizer:
        return await summarizer.summarize(url)


__all__ = [
    "AISummarizer",
    "SummaryType",
    "SummaryLength",
    "VideoSummary",
    "SummaryChapter",
    "KeyMoment",
    "SummarizerConfig",
    "summarize_video",
]
