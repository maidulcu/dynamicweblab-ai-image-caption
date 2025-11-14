"""Core image analysis and captioning engine using BLIP or Moondream models."""
import torch
from PIL import Image
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class ImageAnalyzer:
    """Analyzes images and generates base captions using AI models."""

    def __init__(
        self,
        model_name: str = "Salesforce/blip-image-captioning-large",
        use_moondream: bool = True,
        moondream_model: str = "vikhyatk/moondream2",
        moondream_revision: str = "2025-06-21"
    ):
        """Initialize the image analyzer with specified model.

        Args:
            model_name: HuggingFace model identifier for BLIP captioning
            use_moondream: Whether to use Moondream if available (better quality)
            moondream_model: Moondream model identifier
            moondream_revision: Moondream model revision
        """
        self.blip_model_name = model_name
        self.use_moondream = use_moondream
        self.moondream_model_name = moondream_model
        self.moondream_revision = moondream_revision

        self.processor = None
        self.model = None
        self.model_type = None  # 'moondream' or 'blip'
        self.device = None

        self._load_model()

    def _load_model(self):
        """Load Moondream (preferred) or BLIP model."""
        # Detect device
        if torch.cuda.is_available():
            self.device = "cuda"
            logger.info("GPU detected - CUDA available")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            self.device = "mps"  # Apple Silicon
            logger.info("GPU detected - Apple Silicon (MPS) available")
        else:
            self.device = "cpu"
            logger.info("No GPU detected - using CPU")

        # Try loading Moondream first (better quality)
        if self.use_moondream:
            try:
                logger.info(f"Attempting to load Moondream model: {self.moondream_model_name}")
                from transformers import AutoModelForCausalLM

                self.model = AutoModelForCausalLM.from_pretrained(
                    self.moondream_model_name,
                    revision=self.moondream_revision,
                    trust_remote_code=True,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    device_map={"": self.device}
                )

                self.model_type = "moondream"
                logger.info(f"✓ Moondream model loaded successfully on {self.device.upper()}")
                logger.info("Using Moondream for superior image understanding")
                return

            except Exception as e:
                logger.warning(f"Failed to load Moondream (will fallback to BLIP): {e}")

        # Fallback to BLIP
        try:
            logger.info(f"Loading BLIP model: {self.blip_model_name}")
            from transformers import BlipProcessor, BlipForConditionalGeneration

            self.processor = BlipProcessor.from_pretrained(self.blip_model_name)
            self.model = BlipForConditionalGeneration.from_pretrained(self.blip_model_name)

            # Move to GPU if available
            if self.device != "cpu":
                self.model = self.model.to(self.device)

            self.model_type = "blip"
            logger.info(f"✓ BLIP model loaded successfully on {self.device.upper()}")

        except Exception as e:
            logger.error(f"Error loading BLIP model: {e}")
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

            # Generate base caption (model-specific)
            caption = self._generate_caption(image)

            # Detect objects/elements
            elements = self._detect_elements(caption)

            return {
                "base_caption": caption,
                "dimensions": {"width": width, "height": height},
                "dominant_colors": colors,
                "detected_elements": elements,
                "image_path": image_path,
                "model_used": self.model_type
            }
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            raise

    def _generate_caption(self, image: Image.Image) -> str:
        """Generate a caption for the image using the loaded model.

        Args:
            image: PIL Image object

        Returns:
            Generated caption string
        """
        try:
            if self.model_type == "moondream":
                return self._generate_caption_moondream(image)
            else:
                return self._generate_caption_blip(image)
        except Exception as e:
            logger.error(f"Error generating caption: {e}")
            return "Image"

    def _generate_caption_moondream(self, image: Image.Image) -> str:
        """Generate caption using Moondream model.

        Args:
            image: PIL Image object

        Returns:
            Generated caption string
        """
        try:
            # Moondream has built-in caption method
            result = self.model.caption(
                image,
                length="normal"  # Options: short, normal, long
            )
            caption = result.get("caption", "Image")
            return caption

        except Exception as e:
            logger.error(f"Error with Moondream caption: {e}")
            return "Image"

    def _generate_caption_blip(self, image: Image.Image) -> str:
        """Generate caption using BLIP model.

        Args:
            image: PIL Image object

        Returns:
            Generated caption string
        """
        try:
            # Process image
            inputs = self.processor(image, return_tensors="pt")

            # Move to same device as model
            if self.device != "cpu":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Generate caption
            outputs = self.model.generate(**inputs, max_length=50)
            caption = self.processor.decode(outputs[0], skip_special_tokens=True)

            return caption
        except Exception as e:
            logger.error(f"Error with BLIP caption: {e}")
            return "Image"

    def query_image(self, image: Image.Image, question: str) -> str:
        """Ask a question about the image (Moondream only).

        Args:
            image: PIL Image object
            question: Question to ask about the image

        Returns:
            Answer string
        """
        if self.model_type != "moondream":
            logger.warning("Query feature only available with Moondream model")
            return "Query feature not available with current model"

        try:
            result = self.model.query(image, question)
            return result.get("answer", "Unable to answer")
        except Exception as e:
            logger.error(f"Error querying image: {e}")
            return "Error processing query"

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
                           'silk', 'leather', 'metal', 'wood', 'glass',
                           'person', 'people', 'building', 'car', 'tree']

        elements = [word for word in words if word in element_keywords]
        return list(set(elements))
