# Usage Examples

## Python API Client Example

```python
import requests

# Configuration
API_URL = "http://localhost:8000/api/v1"

def generate_complete_package(image_path, product_info=None, keywords=None):
    """Generate complete package for an image."""

    # Prepare the request
    files = {'image': open(image_path, 'rb')}

    data = {}
    if product_info:
        if 'name' in product_info:
            data['product_name'] = product_info['name']
        if 'category' in product_info:
            data['product_category'] = product_info['category']
        if 'brand' in product_info:
            data['product_brand'] = product_info['brand']
        if 'material' in product_info:
            data['product_material'] = product_info['material']

    if keywords:
        data['keywords'] = ','.join(keywords)

    # Make the request
    response = requests.post(f"{API_URL}/generate/complete", files=files, data=data)

    return response.json()


# Example 1: Basic usage
result = generate_complete_package('product.jpg')
print("Alt-text:", result['alt_text']['standard'])
print("Instagram caption:", result['social_captions']['instagram']['caption'])

# Example 2: With product information
product_info = {
    'name': 'Summer Cotton Dress',
    'category': "Women's Fashion",
    'brand': 'Your Brand',
    'material': 'Cotton'
}

keywords = ['dress', 'summer', 'fashion', 'women', 'cotton']

result = generate_complete_package('dress.jpg', product_info, keywords)

print("\\nComplete Results:")
print("=" * 50)
print("\\nAlt-text:", result['alt_text']['standard'])
print("SEO Score:", result['alt_text']['seo_score'])
print("\\nTitle:", result['seo_metadata']['title'])
print("Meta Description:", result['seo_metadata']['meta_description'])
print("Suggested Filename:", result['seo_metadata']['filename'])

print("\\nSocial Media Captions:")
for platform, caption_data in result['social_captions'].items():
    print(f"\\n{platform.upper()}:")
    print(caption_data['caption'])
    print(f"Engagement Score: {caption_data['engagement_score']}")
```

## JavaScript/Node.js Example

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const API_URL = 'http://localhost:8000/api/v1';

async function generateCompletePackage(imagePath, productInfo = {}, keywords = []) {
    const formData = new FormData();

    // Add image
    formData.append('image', fs.createReadStream(imagePath));

    // Add product info
    if (productInfo.name) formData.append('product_name', productInfo.name);
    if (productInfo.category) formData.append('product_category', productInfo.category);
    if (productInfo.brand) formData.append('product_brand', productInfo.brand);
    if (productInfo.material) formData.append('product_material', productInfo.material);

    // Add keywords
    if (keywords.length > 0) {
        formData.append('keywords', keywords.join(','));
    }

    try {
        const response = await axios.post(`${API_URL}/generate/complete`, formData, {
            headers: formData.getHeaders()
        });

        return response.data;
    } catch (error) {
        console.error('Error:', error.message);
        throw error;
    }
}

// Usage
(async () => {
    const result = await generateCompletePackage('product.jpg', {
        name: 'Cotton Dress',
        category: "Women's Fashion",
        brand: 'My Brand'
    }, ['dress', 'fashion', 'summer']);

    console.log('Alt-text:', result.alt_text.standard);
    console.log('Instagram caption:', result.social_captions.instagram.caption);
})();
```

## cURL Examples

### 1. Generate Complete Package
```bash
curl -X POST "http://localhost:8000/api/v1/generate/complete" \
  -F "image=@product.jpg" \
  -F "product_name=Cotton Dress" \
  -F "product_category=Women's Fashion" \
  -F "product_brand=Your Brand" \
  -F "product_material=Cotton" \
  -F "keywords=dress,fashion,summer,women" \
  -F "platforms=instagram,facebook,twitter"
```

### 2. Generate Alt-Text Only
```bash
curl -X POST "http://localhost:8000/api/v1/generate/alt-text" \
  -F "image=@product.jpg" \
  -F "keywords=dress,fashion" \
  -F "product_category=Women's Fashion"
```

### 3. Generate Social Caption for Specific Platform
```bash
curl -X POST "http://localhost:8000/api/v1/generate/social-caption" \
  -F "image=@product.jpg" \
  -F "platform=instagram" \
  -F "product_name=Cotton Dress" \
  -F "custom_message=New arrival! 🎉" \
  -F "brand_voice=casual_engaging"
```

### 4. Generate SEO Metadata
```bash
curl -X POST "http://localhost:8000/api/v1/generate/seo-metadata" \
  -F "image=@product.jpg" \
  -F "keywords=dress,cotton,summer" \
  -F "product_name=Summer Cotton Dress" \
  -F "url_slug=summer-cotton-dress"
```

### 5. Analyze Image Only
```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "image=@product.jpg"
```

## React Example

```jsx
import React, { useState } from 'react';
import axios from 'axios';

function ImageCaptionGenerator() {
    const [file, setFile] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!file) return;

        const formData = new FormData();
        formData.append('image', file);
        formData.append('product_name', e.target.productName.value);
        formData.append('keywords', e.target.keywords.value);

        setLoading(true);

        try {
            const response = await axios.post(
                'http://localhost:8000/api/v1/generate/complete',
                formData
            );
            setResult(response.data);
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <form onSubmit={handleSubmit}>
                <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => setFile(e.target.files[0])}
                />
                <input name="productName" placeholder="Product Name" />
                <input name="keywords" placeholder="Keywords (comma-separated)" />
                <button type="submit" disabled={loading}>
                    {loading ? 'Generating...' : 'Generate'}
                </button>
            </form>

            {result && (
                <div>
                    <h3>Alt-text:</h3>
                    <p>{result.alt_text.standard}</p>

                    <h3>Instagram Caption:</h3>
                    <p>{result.social_captions.instagram.caption}</p>

                    <h3>SEO Metadata:</h3>
                    <p>Title: {result.seo_metadata.title}</p>
                    <p>Description: {result.seo_metadata.meta_description}</p>
                </div>
            )}
        </div>
    );
}

export default ImageCaptionGenerator;
```

## Batch Processing Example

```python
import requests
from pathlib import Path
import json

API_URL = "http://localhost:8000/api/v1"

def process_image_batch(image_dir, output_file):
    """Process all images in a directory and save results."""

    results = []
    image_files = list(Path(image_dir).glob('*.jpg')) + \
                  list(Path(image_dir).glob('*.png'))

    for image_path in image_files:
        print(f"Processing {image_path.name}...")

        try:
            files = {'image': open(image_path, 'rb')}
            response = requests.post(f"{API_URL}/generate/complete", files=files)

            if response.status_code == 200:
                data = response.json()
                results.append({
                    'filename': image_path.name,
                    'alt_text': data['alt_text']['standard'],
                    'seo_filename': data['seo_metadata']['filename'],
                    'title': data['seo_metadata']['title'],
                    'meta_description': data['seo_metadata']['meta_description'],
                    'instagram_caption': data['social_captions']['instagram']['caption']
                })
                print(f"  ✓ Success")
            else:
                print(f"  ✗ Error: {response.status_code}")

        except Exception as e:
            print(f"  ✗ Error: {e}")

    # Save results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\\nProcessed {len(results)} images. Results saved to {output_file}")
    return results

# Usage
results = process_image_batch('./product_images', 'captions_output.json')
```

## E-commerce Integration Example

```python
class ProductImageProcessor:
    """Process product images for e-commerce platform."""

    def __init__(self, api_url="http://localhost:8000/api/v1"):
        self.api_url = api_url

    def process_product_image(self, image_path, product_data):
        """
        Process a product image and return optimized metadata.

        Args:
            image_path: Path to product image
            product_data: Dict with product info (name, category, etc.)

        Returns:
            Dict with all generated content
        """
        files = {'image': open(image_path, 'rb')}

        data = {
            'product_name': product_data.get('name'),
            'product_category': product_data.get('category'),
            'product_brand': product_data.get('brand'),
            'product_material': product_data.get('material'),
            'keywords': ','.join(product_data.get('keywords', []))
        }

        response = requests.post(
            f"{self.api_url}/generate/complete",
            files=files,
            data=data
        )

        return response.json()

    def update_product_metadata(self, product_id, image_path, product_data):
        """Generate and update product metadata in database."""

        # Generate content
        result = self.process_product_image(image_path, product_data)

        # Extract metadata
        metadata = {
            'alt_text': result['alt_text']['standard'],
            'seo_title': result['seo_metadata']['title'],
            'seo_description': result['seo_metadata']['meta_description'],
            'seo_filename': result['seo_metadata']['filename'],
            'schema_markup': result['seo_metadata']['schema_markup'],
            'social_captions': {}
        }

        # Add social captions
        for platform, caption_data in result['social_captions'].items():
            metadata['social_captions'][platform] = caption_data['caption']

        # Update database (pseudo-code)
        # db.products.update(product_id, metadata)

        return metadata

# Usage
processor = ProductImageProcessor()

product_data = {
    'name': 'Summer Floral Dress',
    'category': "Women's Dresses",
    'brand': 'Fashion Co',
    'material': 'Cotton Blend',
    'keywords': ['dress', 'summer', 'floral', 'women']
}

metadata = processor.update_product_metadata(
    product_id='PROD-123',
    image_path='dress_main.jpg',
    product_data=product_data
)

print("Updated product metadata:")
print(f"Alt-text: {metadata['alt_text']}")
print(f"SEO Title: {metadata['seo_title']}")
```
