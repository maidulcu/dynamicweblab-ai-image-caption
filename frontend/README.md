# AI Caption Frontend (Next.js)

Modern, responsive Next.js frontend for the AI Image Caption Generator with bulk upload support.

## Features

- **Single Image Processing**: Upload and process individual images
- **Bulk Upload**: Process up to 100 images at once with drag-and-drop
- **Real-time Progress**: Live progress tracking for batch operations
- **Export Results**: Download batch results as CSV or JSON
- **Modern UI**: Built with Tailwind CSS and Lucide icons
- **Responsive Design**: Works on desktop, tablet, and mobile

## Tech Stack

- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS
- react-dropzone (drag-and-drop)
- axios (API calls)
- lucide-react (icons)

## Installation

```bash
cd frontend
npm install
```

## Development

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

**Note**: Make sure the FastAPI backend is running at `http://localhost:8000`

## Building for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home page
│   ├── single/
│   │   └── page.tsx        # Single image upload
│   ├── batch/
│   │   └── page.tsx        # Bulk upload
│   └── globals.css         # Global styles
├── public/                 # Static assets
├── package.json
├── next.config.js
├── tailwind.config.js
└── tsconfig.json
```

## Pages

### Home Page (`/`)
- Feature showcase
- Technology stack overview
- Quick links to single and batch processing

### Single Upload (`/single`)
- Upload single image
- Enter product details
- View results in tabbed interface (Alt Text, Social, SEO)

### Batch Upload (`/batch`)
- Drag-and-drop multiple images
- Real-time progress tracking
- Export results as CSV or JSON
- Processing up to 100 images in parallel

## Configuration

### API URL
The API URL is configured in `next.config.js`:

```javascript
async rewrites() {
  return [
    {
      source: '/api/v1/:path*',
      destination: 'http://localhost:8000/api/v1/:path*',
    },
  ]
}
```

Change the `destination` URL if your backend runs on a different host/port.

## Environment Variables

Create `.env.local` if needed:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Styling

The frontend uses Tailwind CSS with a custom purple/primary color scheme:

- Primary: `#667eea`
- Secondary: `#764ba2`
- Gradient: From primary to purple

Customize colors in `tailwind.config.js`.

## Features in Detail

### Bulk Upload
- Supports up to 100 images per batch
- Drag-and-drop interface
- Image preview grid
- Remove individual images
- Progress bar with percentage
- Success/failure stats
- Estimated completion time

### Export Options
- CSV: Tabular format with all metadata
- JSON: Complete data structure

### Real-time Updates
- Polls batch status every 2 seconds
- Shows live progress
- Updates statistics
- Handles completion automatically

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance

- Lazy loading for images
- Optimized bundle size
- Fast API calls with axios
- Efficient re-renders with React hooks

## License

MIT
