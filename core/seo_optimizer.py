"""SEO optimizer for image metadata and content."""
import logging
from typing import Dict, List, Optional
import re

logger = logging.getLogger(__name__)


class SEOOptimizer:
    """Optimizes image metadata for search engine visibility."""

    def __init__(self):
        """Initialize the SEO optimizer."""
        # Common SEO keywords for e-commerce
        self.ecommerce_keywords = [
            "buy", "shop", "online", "sale", "deal", "discount",
            "quality", "premium", "best", "top", "new", "latest"
        ]

    def optimize_metadata(
        self,
        image_analysis: Dict,
        alt_text: str,
        product_info: Optional[Dict] = None,
        target_keywords: Optional[List[str]] = None,
        url_slug: Optional[str] = None
    ) -> Dict[str, any]:
        """Generate comprehensive SEO-optimized metadata.

        Args:
            image_analysis: Image analysis results
            alt_text: Generated alt-text
            product_info: Product information
            target_keywords: Target SEO keywords
            url_slug: URL slug for the image/product

        Returns:
            Dictionary with SEO metadata
        """
        try:
            # Extract base information
            base_caption = image_analysis.get("base_caption", "")
            colors = image_analysis.get("dominant_colors", [])

            # Generate filename suggestion
            filename = self._generate_seo_filename(
                product_info, colors, url_slug
            )

            # Generate title tag
            title = self._generate_title_tag(
                product_info, base_caption, alt_text
            )

            # Generate meta description
            meta_description = self._generate_meta_description(
                product_info, alt_text, target_keywords
            )

            # Generate Open Graph tags
            og_tags = self._generate_og_tags(
                title, meta_description, image_analysis
            )

            # Generate schema.org markup
            schema_markup = self._generate_schema_markup(
                product_info, image_analysis, alt_text
            )

            # Keyword analysis
            keyword_analysis = self._analyze_keywords(
                alt_text, title, meta_description, target_keywords
            )

            # Calculate overall SEO score
            seo_score = self._calculate_overall_seo_score(
                filename, alt_text, title, meta_description,
                keyword_analysis, target_keywords
            )

            return {
                "filename": filename,
                "alt_text": alt_text,
                "title": title,
                "meta_description": meta_description,
                "og_tags": og_tags,
                "schema_markup": schema_markup,
                "keyword_analysis": keyword_analysis,
                "seo_score": seo_score,
                "recommendations": self._generate_recommendations(
                    seo_score, keyword_analysis
                )
            }
        except Exception as e:
            logger.error(f"Error optimizing metadata: {e}")
            return {
                "filename": "image.jpg",
                "alt_text": alt_text,
                "title": alt_text,
                "meta_description": alt_text,
                "og_tags": {},
                "schema_markup": {},
                "keyword_analysis": {},
                "seo_score": 0,
                "recommendations": ["Error optimizing metadata"]
            }

    def _generate_seo_filename(
        self,
        product_info: Optional[Dict],
        colors: List[str],
        url_slug: Optional[str]
    ) -> str:
        """Generate SEO-friendly filename.

        Args:
            product_info: Product information
            colors: Dominant colors
            url_slug: Existing URL slug

        Returns:
            SEO-optimized filename
        """
        parts = []

        if url_slug:
            # Clean existing slug
            slug = re.sub(r'[^a-z0-9-]', '', url_slug.lower())
            parts.append(slug)
        elif product_info:
            # Build from product info
            if "category" in product_info:
                parts.append(product_info["category"].lower().replace(" ", "-"))
            if "name" in product_info:
                parts.append(product_info["name"].lower().replace(" ", "-"))

        # Add color if available
        if colors and len(parts) < 3:
            parts.append(colors[0].lower())

        # Default if no parts
        if not parts:
            parts = ["product", "image"]

        filename = "-".join(parts)

        # Clean up
        filename = re.sub(r'[^a-z0-9-]', '', filename)
        filename = re.sub(r'-+', '-', filename)  # Remove multiple dashes
        filename = filename.strip('-')[:50]  # Limit length

        return f"{filename}.jpg"

    def _generate_title_tag(
        self,
        product_info: Optional[Dict],
        base_caption: str,
        alt_text: str
    ) -> str:
        """Generate optimized title tag (50-60 characters ideal).

        Args:
            product_info: Product information
            base_caption: Base caption
            alt_text: Alt-text

        Returns:
            Title tag
        """
        if product_info and "name" in product_info:
            title = product_info["name"]
            if "brand" in product_info:
                title = f"{product_info['brand']} {title}"
        else:
            # Use alt-text or caption
            title = alt_text or base_caption

        # Add category if space permits and available
        if product_info and "category" in product_info and len(title) < 40:
            title = f"{title} - {product_info['category']}"

        # Truncate to optimal length
        if len(title) > 60:
            title = title[:57] + "..."

        return title

    def _generate_meta_description(
        self,
        product_info: Optional[Dict],
        alt_text: str,
        keywords: Optional[List[str]] = None
    ) -> str:
        """Generate meta description (150-160 characters ideal).

        Args:
            product_info: Product information
            alt_text: Alt-text
            keywords: Target keywords

        Returns:
            Meta description
        """
        parts = []

        # Start with descriptive text
        parts.append(alt_text)

        # Add product details
        if product_info:
            if "features" in product_info:
                parts.append(product_info["features"])
            if "material" in product_info:
                parts.append(f"Made from {product_info['material']}")

        # Add CTA with keywords
        cta_keywords = ["Shop", "Buy online"]
        if keywords:
            # Use first keyword if it's action-oriented
            keyword = keywords[0]
            if keyword.lower() in self.ecommerce_keywords:
                cta_keywords.insert(0, keyword.title())

        parts.append(f"{cta_keywords[0]} now.")

        # Combine and optimize length
        description = ". ".join(parts)

        if len(description) > 160:
            description = description[:157] + "..."

        return description

    def _generate_og_tags(
        self,
        title: str,
        description: str,
        image_analysis: Dict
    ) -> Dict[str, str]:
        """Generate Open Graph meta tags for social sharing.

        Args:
            title: Page title
            description: Meta description
            image_analysis: Image analysis data

        Returns:
            Dictionary of OG tags
        """
        dims = image_analysis.get("dimensions", {})

        return {
            "og:title": title,
            "og:description": description,
            "og:type": "product",
            "og:image:alt": title,
            "og:image:width": str(dims.get("width", 1200)),
            "og:image:height": str(dims.get("height", 630)),
        }

    def _generate_schema_markup(
        self,
        product_info: Optional[Dict],
        image_analysis: Dict,
        alt_text: str
    ) -> Dict:
        """Generate Schema.org structured data markup.

        Args:
            product_info: Product information
            image_analysis: Image analysis data
            alt_text: Alt-text

        Returns:
            Schema.org JSON-LD markup
        """
        schema = {
            "@context": "https://schema.org/",
            "@type": "ImageObject",
            "contentUrl": "{{IMAGE_URL}}",  # Placeholder
            "description": alt_text,
        }

        # Add dimensions
        dims = image_analysis.get("dimensions", {})
        if dims:
            schema["width"] = dims.get("width")
            schema["height"] = dims.get("height")

        # Add product context if available
        if product_info:
            schema["about"] = {
                "@type": "Product",
                "name": product_info.get("name", "Product"),
            }

            if "brand" in product_info:
                schema["about"]["brand"] = {
                    "@type": "Brand",
                    "name": product_info["brand"]
                }

        return schema

    def _analyze_keywords(
        self,
        alt_text: str,
        title: str,
        description: str,
        target_keywords: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """Analyze keyword usage across metadata.

        Args:
            alt_text: Alt-text
            title: Title tag
            description: Meta description
            target_keywords: Target keywords

        Returns:
            Keyword analysis results
        """
        if not target_keywords:
            target_keywords = []

        # Combine all text
        all_text = f"{alt_text} {title} {description}".lower()

        # Check keyword presence
        keyword_presence = {}
        for keyword in target_keywords:
            keyword_presence[keyword] = keyword.lower() in all_text

        # Calculate keyword density
        words = all_text.split()
        total_words = len(words)

        keyword_density = {}
        for keyword in target_keywords:
            count = all_text.count(keyword.lower())
            density = (count / total_words * 100) if total_words > 0 else 0
            keyword_density[keyword] = round(density, 2)

        # Find used keywords
        used_keywords = [kw for kw, present in keyword_presence.items() if present]
        missing_keywords = [kw for kw, present in keyword_presence.items() if not present]

        return {
            "target_keywords": target_keywords,
            "used_keywords": used_keywords,
            "missing_keywords": missing_keywords,
            "keyword_presence": keyword_presence,
            "keyword_density": keyword_density,
            "coverage": len(used_keywords) / len(target_keywords) * 100 if target_keywords else 0
        }

    def _calculate_overall_seo_score(
        self,
        filename: str,
        alt_text: str,
        title: str,
        description: str,
        keyword_analysis: Dict,
        target_keywords: Optional[List[str]] = None
    ) -> int:
        """Calculate overall SEO score (0-100).

        Args:
            filename: Generated filename
            alt_text: Alt-text
            title: Title tag
            description: Meta description
            keyword_analysis: Keyword analysis results
            target_keywords: Target keywords

        Returns:
            SEO score
        """
        score = 0

        # Filename score (descriptive, uses hyphens)
        if len(filename) > 10 and '-' in filename:
            score += 10

        # Alt-text score (50-125 chars)
        alt_len = len(alt_text)
        if 50 <= alt_len <= 125:
            score += 20
        elif 30 <= alt_len < 50:
            score += 15

        # Title score (50-60 chars)
        title_len = len(title)
        if 50 <= title_len <= 60:
            score += 20
        elif 40 <= title_len < 70:
            score += 15

        # Description score (150-160 chars)
        desc_len = len(description)
        if 150 <= desc_len <= 160:
            score += 20
        elif 130 <= desc_len < 170:
            score += 15

        # Keyword coverage
        if target_keywords:
            coverage = keyword_analysis.get("coverage", 0)
            score += int(coverage * 0.3)  # Up to 30 points

        return min(score, 100)

    def _generate_recommendations(
        self,
        seo_score: int,
        keyword_analysis: Dict
    ) -> List[str]:
        """Generate SEO improvement recommendations.

        Args:
            seo_score: Current SEO score
            keyword_analysis: Keyword analysis results

        Returns:
            List of recommendations
        """
        recommendations = []

        if seo_score < 70:
            recommendations.append(
                "Overall SEO score could be improved. Review metadata completeness."
            )

        missing = keyword_analysis.get("missing_keywords", [])
        if missing:
            recommendations.append(
                f"Consider adding these keywords: {', '.join(missing[:3])}"
            )

        coverage = keyword_analysis.get("coverage", 0)
        if coverage < 50:
            recommendations.append(
                "Low keyword coverage. Incorporate more target keywords naturally."
            )

        if not recommendations:
            recommendations.append("SEO optimization looks good!")

        return recommendations
