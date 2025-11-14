"""Alt-text generator for accessibility and SEO optimization."""
import logging
from typing import Dict, List, Optional
import re

logger = logging.getLogger(__name__)


class AltTextGenerator:
    """Generates SEO-optimized alt-text for product images."""

    def __init__(self, max_length: int = 125):
        """Initialize the alt-text generator.

        Args:
            max_length: Maximum character length for alt-text (SEO best practice: 125)
        """
        self.max_length = max_length

    def generate_alt_text(
        self,
        image_analysis: Dict,
        keywords: Optional[List[str]] = None,
        product_info: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Generate descriptive, keyword-rich alt-text.

        Args:
            image_analysis: Analysis results from ImageAnalyzer
            keywords: List of SEO keywords to incorporate
            product_info: Additional product information (name, category, etc.)

        Returns:
            Dictionary with alt-text variations
        """
        try:
            base_caption = image_analysis.get("base_caption", "")
            colors = image_analysis.get("dominant_colors", [])
            elements = image_analysis.get("detected_elements", [])

            # Build comprehensive description
            parts = []

            # Add colors
            if colors:
                color_text = " ".join(colors[:2])  # Use top 2 colors
                parts.append(color_text)

            # Add product info if available
            if product_info:
                if "category" in product_info:
                    parts.append(product_info["category"])
                if "name" in product_info:
                    parts.append(product_info["name"])
                if "material" in product_info:
                    parts.append(product_info["material"])
                if "style" in product_info:
                    parts.append(product_info["style"])

            # Add base caption elements
            if base_caption:
                # Clean and add relevant parts
                caption_words = self._extract_relevant_words(base_caption)
                parts.extend(caption_words)

            # Add detected elements
            if elements:
                parts.extend(elements)

            # Build alt-text
            alt_text = self._build_optimized_text(parts, keywords)

            # Create variations
            short_alt = self._truncate_text(alt_text, 50)
            medium_alt = self._truncate_text(alt_text, 100)

            return {
                "standard": alt_text,
                "short": short_alt,
                "medium": medium_alt,
                "descriptive": self._enhance_description(alt_text, image_analysis),
                "length": len(alt_text),
                "seo_score": self._calculate_seo_score(alt_text, keywords)
            }
        except Exception as e:
            logger.error(f"Error generating alt-text: {e}")
            return {
                "standard": "Product image",
                "short": "Product",
                "medium": "Product image",
                "descriptive": "Product image",
                "length": 13,
                "seo_score": 0
            }

    def _extract_relevant_words(self, text: str) -> List[str]:
        """Extract relevant descriptive words from text.

        Args:
            text: Input text

        Returns:
            List of relevant words
        """
        # Remove common stop words
        stop_words = {'a', 'an', 'the', 'is', 'are', 'in', 'on', 'at', 'to',
                     'for', 'of', 'with', 'by', 'from'}

        words = text.lower().split()
        relevant = [w for w in words if w not in stop_words and len(w) > 2]
        return relevant

    def _build_optimized_text(
        self,
        parts: List[str],
        keywords: Optional[List[str]] = None
    ) -> str:
        """Build optimized alt-text from parts and keywords.

        Args:
            parts: List of text parts to combine
            keywords: SEO keywords to incorporate

        Returns:
            Optimized alt-text string
        """
        # Remove duplicates while preserving order
        seen = set()
        unique_parts = []
        for part in parts:
            part_lower = part.lower()
            if part_lower not in seen:
                seen.add(part_lower)
                unique_parts.append(part)

        # Add keywords that aren't already present
        if keywords:
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower not in seen:
                    unique_parts.append(keyword)
                    seen.add(keyword_lower)

        # Join parts intelligently
        text = " ".join(unique_parts)

        # Capitalize first letter
        text = text.strip()
        if text:
            text = text[0].upper() + text[1:]

        # Truncate if too long
        if len(text) > self.max_length:
            text = self._truncate_text(text, self.max_length)

        return text

    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text intelligently at word boundaries.

        Args:
            text: Text to truncate
            max_length: Maximum length

        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text

        # Find last space before max_length
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')

        if last_space > 0:
            return truncated[:last_space]
        else:
            return truncated

    def _enhance_description(self, alt_text: str, analysis: Dict) -> str:
        """Create enhanced descriptive version with more detail.

        Args:
            alt_text: Base alt-text
            analysis: Image analysis data

        Returns:
            Enhanced description
        """
        enhanced = alt_text

        # Add dimension info for context
        dims = analysis.get("dimensions", {})
        if dims:
            aspect = "landscape" if dims.get("width", 0) > dims.get("height", 0) else "portrait"
            enhanced = f"{enhanced} in {aspect} orientation"

        return enhanced

    def _calculate_seo_score(self, alt_text: str, keywords: Optional[List[str]] = None) -> int:
        """Calculate SEO effectiveness score (0-100).

        Args:
            alt_text: Generated alt-text
            keywords: Target keywords

        Returns:
            SEO score
        """
        score = 0

        # Length score (optimal: 50-125 characters)
        length = len(alt_text)
        if 50 <= length <= 125:
            score += 30
        elif 30 <= length < 50:
            score += 20
        elif length > 125:
            score += 10

        # Keyword presence
        if keywords:
            alt_lower = alt_text.lower()
            keyword_count = sum(1 for kw in keywords if kw.lower() in alt_lower)
            score += min(keyword_count * 15, 40)

        # Descriptiveness (word count)
        word_count = len(alt_text.split())
        if 5 <= word_count <= 15:
            score += 30
        elif 3 <= word_count < 5:
            score += 20

        return min(score, 100)

    def generate_batch(
        self,
        image_analyses: List[Dict],
        keywords: Optional[List[str]] = None,
        product_infos: Optional[List[Dict]] = None
    ) -> List[Dict[str, str]]:
        """Generate alt-text for multiple images.

        Args:
            image_analyses: List of image analysis results
            keywords: Common keywords for all images
            product_infos: List of product info dicts (optional)

        Returns:
            List of alt-text dictionaries
        """
        results = []
        for i, analysis in enumerate(image_analyses):
            product_info = product_infos[i] if product_infos and i < len(product_infos) else None
            alt_text = self.generate_alt_text(analysis, keywords, product_info)
            results.append(alt_text)

        return results
