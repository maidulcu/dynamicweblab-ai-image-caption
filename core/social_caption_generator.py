"""Social media caption generator with platform-specific optimization."""
import logging
from typing import Dict, List, Optional
from enum import Enum
import random

logger = logging.getLogger(__name__)


class SocialPlatform(Enum):
    """Supported social media platforms."""
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"


class SocialCaptionGenerator:
    """Generates engaging, platform-optimized social media captions."""

    # Platform-specific configurations
    PLATFORM_CONFIGS = {
        SocialPlatform.INSTAGRAM: {
            "max_length": 2200,
            "max_hashtags": 30,
            "optimal_hashtags": 11,
            "emoji_friendly": True,
            "style": "casual_engaging"
        },
        SocialPlatform.TWITTER: {
            "max_length": 280,
            "max_hashtags": 2,
            "optimal_hashtags": 1,
            "emoji_friendly": True,
            "style": "concise_witty"
        },
        SocialPlatform.FACEBOOK: {
            "max_length": 63206,
            "max_hashtags": 3,
            "optimal_hashtags": 2,
            "emoji_friendly": True,
            "style": "conversational"
        },
        SocialPlatform.LINKEDIN: {
            "max_length": 3000,
            "max_hashtags": 5,
            "optimal_hashtags": 3,
            "emoji_friendly": False,
            "style": "professional"
        },
        SocialPlatform.PINTEREST: {
            "max_length": 500,
            "max_hashtags": 20,
            "optimal_hashtags": 10,
            "emoji_friendly": True,
            "style": "descriptive_inspiring"
        }
    }

    # Engaging call-to-action phrases
    CTAS = {
        "casual_engaging": [
            "Shop now! Link in bio",
            "Tap to shop",
            "Get yours today",
            "Available now",
            "Limited stock - don't miss out",
            "Swipe up to shop",
            "DM us to order"
        ],
        "concise_witty": [
            "Shop the look",
            "Link below",
            "Get it now",
            "Must-have alert"
        ],
        "conversational": [
            "Click to shop",
            "Check it out",
            "See more details",
            "Learn more"
        ],
        "professional": [
            "View product details",
            "Explore our collection",
            "Discover more"
        ],
        "descriptive_inspiring": [
            "Pin to save for later",
            "Click for details",
            "Shop this look",
            "Get inspired"
        ]
    }

    def generate_caption(
        self,
        image_analysis: Dict,
        platform: SocialPlatform,
        product_info: Optional[Dict[str, str]] = None,
        brand_voice: Optional[str] = None,
        include_hashtags: bool = True,
        custom_message: Optional[str] = None
    ) -> Dict[str, any]:
        """Generate platform-optimized social media caption.

        Args:
            image_analysis: Analysis results from ImageAnalyzer
            platform: Target social media platform
            product_info: Product details
            brand_voice: Brand voice/tone preference
            include_hashtags: Whether to include hashtags
            custom_message: Custom message to incorporate

        Returns:
            Dictionary with caption and metadata
        """
        try:
            config = self.PLATFORM_CONFIGS[platform]
            style = brand_voice or config["style"]

            # Build caption components
            main_text = self._create_main_text(
                image_analysis, product_info, style, config["max_length"]
            )

            # Add custom message if provided
            if custom_message:
                main_text = f"{custom_message}\n\n{main_text}"

            # Generate hashtags
            hashtags = []
            if include_hashtags:
                hashtags = self._generate_hashtags(
                    image_analysis,
                    product_info,
                    config["optimal_hashtags"],
                    platform
                )

            # Add call-to-action
            cta = self._get_cta(style)

            # Combine components
            caption = self._assemble_caption(
                main_text, hashtags, cta, config["max_length"]
            )

            # Calculate engagement score
            engagement_score = self._calculate_engagement_score(
                caption, hashtags, config
            )

            return {
                "caption": caption,
                "platform": platform.value,
                "length": len(caption),
                "hashtags": hashtags,
                "hashtag_count": len(hashtags),
                "engagement_score": engagement_score,
                "has_cta": bool(cta),
                "truncated": len(caption) >= config["max_length"]
            }
        except Exception as e:
            logger.error(f"Error generating social caption: {e}")
            return {
                "caption": image_analysis.get("base_caption", "Check this out!"),
                "platform": platform.value,
                "length": 0,
                "hashtags": [],
                "hashtag_count": 0,
                "engagement_score": 0,
                "has_cta": False,
                "truncated": False
            }

    def _create_main_text(
        self,
        analysis: Dict,
        product_info: Optional[Dict],
        style: str,
        max_length: int
    ) -> str:
        """Create the main caption text.

        Args:
            analysis: Image analysis data
            product_info: Product information
            style: Writing style
            max_length: Maximum allowed length

        Returns:
            Main caption text
        """
        base_caption = analysis.get("base_caption", "")
        colors = analysis.get("dominant_colors", [])

        # Style-specific templates
        if style == "casual_engaging":
            templates = [
                "Obsessed with this {colors} {item}! 💕",
                "Just dropped: {colors} {item} ✨",
                "Can't get enough of this {colors} {item}! 😍",
                "New favorite: {colors} {item}",
            ]
        elif style == "concise_witty":
            templates = [
                "{colors} {item} hitting different 🔥",
                "The {colors} {item} you need",
                "{colors} {item} = instant mood boost",
            ]
        elif style == "professional":
            templates = [
                "Introducing our {colors} {item}",
                "Premium {colors} {item} - crafted with care",
                "Elevate your style with this {colors} {item}",
            ]
        elif style == "descriptive_inspiring":
            templates = [
                "Beautiful {colors} {item} to inspire your next look",
                "Stunning {colors} {item} perfect for any occasion",
            ]
        else:  # conversational
            templates = [
                "Check out this amazing {colors} {item}!",
                "Looking for the perfect {item}? This {colors} one is it!",
                "We're loving this {colors} {item}",
            ]

        # Fill template
        item = "piece"
        if product_info:
            item = product_info.get("category", product_info.get("name", "piece"))

        color_text = " and ".join(colors[:2]) if colors else ""

        template = random.choice(templates)
        text = template.format(colors=color_text, item=item)

        # Add product details if available and space permits
        if product_info and len(text) < max_length * 0.5:
            details = []
            if "material" in product_info:
                details.append(f"{product_info['material']}")
            if "features" in product_info:
                details.append(product_info["features"])

            if details:
                text += f" {' | '.join(details)}"

        return text

    def _generate_hashtags(
        self,
        analysis: Dict,
        product_info: Optional[Dict],
        target_count: int,
        platform: SocialPlatform
    ) -> List[str]:
        """Generate relevant hashtags for the caption.

        Args:
            analysis: Image analysis data
            product_info: Product information
            target_count: Target number of hashtags
            platform: Social media platform

        Returns:
            List of hashtags
        """
        hashtags = set()

        # Platform-specific popular tags
        platform_tags = {
            SocialPlatform.INSTAGRAM: ["#instagood", "#photooftheday", "#fashion"],
            SocialPlatform.TWITTER: ["#fashion", "#style"],
            SocialPlatform.FACEBOOK: ["#shopping", "#fashion"],
            SocialPlatform.LINKEDIN: ["#business", "#professional"],
            SocialPlatform.PINTEREST: ["#inspiration", "#ideas", "#diy"]
        }

        # Add platform-specific tags
        if platform in platform_tags:
            hashtags.update(platform_tags[platform][:1])

        # Add product-based tags
        if product_info:
            if "category" in product_info:
                category = product_info["category"].replace(" ", "")
                hashtags.add(f"#{category.lower()}")

            if "style" in product_info:
                style = product_info["style"].replace(" ", "")
                hashtags.add(f"#{style.lower()}")

            if "brand" in product_info:
                brand = product_info["brand"].replace(" ", "")
                hashtags.add(f"#{brand.lower()}")

        # Add color-based tags
        colors = analysis.get("dominant_colors", [])
        for color in colors[:2]:
            hashtags.add(f"#{color}style")

        # Add common shopping tags
        shopping_tags = [
            "#shopnow", "#onlineshopping", "#sale", "#trending",
            "#musthave", "#newcollection", "#style", "#fashion"
        ]
        hashtags.update(random.sample(shopping_tags, min(3, target_count)))

        # Convert to list and limit to target
        hashtag_list = list(hashtags)[:target_count]

        return sorted(hashtag_list)

    def _get_cta(self, style: str) -> str:
        """Get appropriate call-to-action for the style.

        Args:
            style: Writing style

        Returns:
            CTA string
        """
        ctas = self.CTAS.get(style, self.CTAS["casual_engaging"])
        return random.choice(ctas)

    def _assemble_caption(
        self,
        main_text: str,
        hashtags: List[str],
        cta: str,
        max_length: int
    ) -> str:
        """Assemble final caption from components.

        Args:
            main_text: Main caption text
            hashtags: List of hashtags
            cta: Call-to-action text
            max_length: Maximum length

        Returns:
            Complete caption
        """
        # Build caption parts
        parts = [main_text]

        if cta:
            parts.append(f"\n\n{cta}")

        if hashtags:
            hashtag_text = " ".join(hashtags)
            parts.append(f"\n\n{hashtag_text}")

        caption = "".join(parts)

        # Truncate if needed
        if len(caption) > max_length:
            # Remove hashtags first if too long
            caption = f"{main_text}\n\n{cta}" if cta else main_text
            if len(caption) > max_length:
                caption = caption[:max_length-3] + "..."

        return caption.strip()

    def _calculate_engagement_score(
        self,
        caption: str,
        hashtags: List[str],
        config: Dict
    ) -> int:
        """Calculate predicted engagement score (0-100).

        Args:
            caption: Final caption
            hashtags: List of hashtags
            config: Platform configuration

        Returns:
            Engagement score
        """
        score = 0

        # Length score (optimal: not too short, not too long)
        length = len(caption)
        if config["max_length"] * 0.2 <= length <= config["max_length"] * 0.8:
            score += 30
        else:
            score += 15

        # Hashtag score (using optimal number)
        hashtag_count = len(hashtags)
        if hashtag_count == config["optimal_hashtags"]:
            score += 25
        elif abs(hashtag_count - config["optimal_hashtags"]) <= 2:
            score += 15

        # Has question mark (engagement booster)
        if "?" in caption:
            score += 10

        # Has emoji (if platform is emoji-friendly)
        emoji_pattern = r'[😀-🙏🌀-🗿🚀-🛿]'
        import re
        if re.search(emoji_pattern, caption) and config["emoji_friendly"]:
            score += 15

        # Has CTA
        cta_keywords = ["shop", "link", "tap", "click", "swipe", "dm", "check"]
        if any(keyword in caption.lower() for keyword in cta_keywords):
            score += 20

        return min(score, 100)

    def generate_multi_platform(
        self,
        image_analysis: Dict,
        product_info: Optional[Dict[str, str]] = None,
        platforms: Optional[List[SocialPlatform]] = None
    ) -> Dict[str, Dict]:
        """Generate captions for multiple platforms at once.

        Args:
            image_analysis: Image analysis results
            product_info: Product information
            platforms: List of platforms (defaults to all)

        Returns:
            Dictionary mapping platform names to caption data
        """
        if platforms is None:
            platforms = list(SocialPlatform)

        results = {}
        for platform in platforms:
            caption_data = self.generate_caption(
                image_analysis, platform, product_info
            )
            results[platform.value] = caption_data

        return results
