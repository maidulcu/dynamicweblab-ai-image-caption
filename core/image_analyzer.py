"""Core image analysis and captioning engine using BLIP model."""
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class ImageAnalyzer:
    """Analyzes images and generates base captions using AI models."""

    def __init__(self, model_name: str = "Salesforce/blip-image-captioning-large"):
        """Initialize the image analyzer with specified model.

        Args:
            model_name: HuggingFace model identifier for image captioning
        """
        self.model_name = model_name
        self.processor = None
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the BLIP model and processor."""
        try:
            logger.info(f"Loading model: {self.model_name}")
            self.processor = BlipProcessor.from_pretrained(self.model_name)
            self.model = BlipForConditionalGeneration.from_pretrained(self.model_name)

            # Move to GPU if available
            if torch.cuda.is_available():
                self.model = self.model.to("cuda")
                logger.info("Model loaded on GPU")
            else:
                logger.info("Model loaded on CPU")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise

    def analyze_image(self, image_path: str) -> Dict[str, any]:
        """Analyze an image and extract visual features.

        Args:
            image_path: Path to the image file

        Returns:
            Dictionary containing image analysis results
        """
        try:
            # Load and process image
            image = Image.open(image_path).convert('RGB')

            # Get image dimensions
            width, height = image.size

            # Detect dominant colors
            colors = self._detect_colors(image)

            # Generate base caption
            caption = self._generate_caption(image)

            # Detect objects/elements
            elements = self._detect_elements(caption)

            return {
                "base_caption": caption,
                "dimensions": {"width": width, "height": height},
                "dominant_colors": colors,
                "detected_elements": elements,
                "image_path": image_path
            }
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            raise

    def _generate_caption(self, image: Image.Image) -> str:
        """Generate a caption for the image using BLIP model.

        Args:
            image: PIL Image object

        Returns:
            Generated caption string
        """
        try:
            # Process image
            inputs = self.processor(image, return_tensors="pt")

            # Move to same device as model
            if torch.cuda.is_available():
                inputs = {k: v.to("cuda") for k, v in inputs.items()}

            # Generate caption
            outputs = self.model.generate(**inputs, max_length=50)
            caption = self.processor.decode(outputs[0], skip_special_tokens=True)

            return caption
        except Exception as e:
            logger.error(f"Error generating caption: {e}")
            return "Image"

    def _detect_colors(self, image: Image.Image, num_colors: int = 3) -> List[str]:
        """Detect dominant colors in the image.

        Args:
            image: PIL Image object
            num_colors: Number of dominant colors to detect

        Returns:
            List of color names
        """
        try:
            # Resize for faster processing
            small_image = image.resize((150, 150))

            # Get colors from image
            colors = small_image.getcolors(150 * 150)
            if not colors:
                return []

            # Sort by frequency
            sorted_colors = sorted(colors, key=lambda x: x[0], reverse=True)

            # Convert RGB to color names (simplified)
            color_names = []
            for count, rgb in sorted_colors[:num_colors]:
                color_name = self._rgb_to_color_name(rgb)
                if color_name and color_name not in color_names:
                    color_names.append(color_name)

            return color_names[:num_colors]
        except Exception as e:
            logger.error(f"Error detecting colors: {e}")
            return []

    def _rgb_to_color_name(self, rgb: tuple) -> Optional[str]:
        """Convert RGB values to approximate color name.

        Args:
            rgb: Tuple of (R, G, B) values

        Returns:
            Color name string
        """
        r, g, b = rgb[:3] if len(rgb) > 3 else rgb

        # Simple color detection logic
        if r > 200 and g > 200 and b > 200:
            return "white"
        elif r < 50 and g < 50 and b < 50:
            return "black"
        elif r > g and r > b:
            if r > 200:
                return "red"
            return "burgundy"
        elif g > r and g > b:
            if g > 200:
                return "green"
            return "olive"
        elif b > r and b > g:
            if b > 200:
                return "blue"
            return "navy"
        elif r > 150 and g > 150 and b < 100:
            return "yellow"
        elif r > 150 and g < 100 and b > 150:
            return "purple"
        elif r < 100 and g > 100 and b > 150:
            return "cyan"
        else:
            return "multicolor"

    def _detect_elements(self, caption: str) -> List[str]:
        """Extract key elements from the caption.

        Args:
            caption: Generated caption string

        Returns:
            List of detected elements
        """
        # Extract nouns and key descriptive words
        words = caption.lower().split()

        # Common product/image elements
        element_keywords = ['dress', 'shirt', 'pants', 'shoes', 'bag', 'hat',
                           'flower', 'pattern', 'design', 'fabric', 'cotton',
                           'silk', 'leather', 'metal', 'wood', 'glass']

        elements = [word for word in words if word in element_keywords]
        return list(set(elements))
