"""Batch processing utilities for handling large image inventories."""
import asyncio
import logging
import shutil
from typing import List, Dict, Optional, Callable
from pathlib import Path
import csv
import json
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Process multiple images in batches with progress tracking."""

    def __init__(self, max_concurrent: int = 5):
        """Initialize batch processor.

        Args:
            max_concurrent: Maximum number of concurrent processing tasks
        """
        self.max_concurrent = max_concurrent
        self.active_batches = {}

    async def process_batch(
        self,
        image_paths: List[str],
        process_func: Callable,
        product_infos: Optional[List[Dict]] = None,
        keywords: Optional[List[str]] = None,
        batch_id: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
        cleanup_files: bool = True
    ) -> Dict:
        """Process multiple images in parallel batches.

        Args:
            image_paths: List of image file paths
            process_func: Function to process each image
            product_infos: Optional list of product info dicts
            keywords: Common keywords for all images
            batch_id: Optional batch identifier
            progress_callback: Optional callback for progress updates
            cleanup_files: Whether to delete files after processing

        Returns:
            Dictionary with batch results
        """
        if batch_id is None:
            batch_id = str(uuid.uuid4())

        total_images = len(image_paths)
        batch_dir = None

        # Determine batch directory from first image path
        if image_paths and cleanup_files:
            first_path = Path(image_paths[0])
            batch_dir = first_path.parent

        # Initialize batch tracking
        batch_data = {
            "batch_id": batch_id,
            "total_images": total_images,
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "results": [],
            "errors": [],
            "start_time": datetime.utcnow().isoformat(),
            "status": "processing"
        }

        self.active_batches[batch_id] = batch_data

        try:
            # Create processing tasks
            semaphore = asyncio.Semaphore(self.max_concurrent)

            async def process_with_semaphore(idx: int, image_path: str):
                """Process single image with semaphore control."""
                async with semaphore:
                    try:
                        # Get product info if available
                        product_info = None
                        if product_infos and idx < len(product_infos):
                            product_info = product_infos[idx]

                        # Process image
                        result = await process_func(
                            image_path,
                            product_info=product_info,
                            keywords=keywords
                        )

                        # Update batch data
                        batch_data["results"].append({
                            "index": idx,
                            "image_path": image_path,
                            "success": True,
                            "data": result
                        })
                        batch_data["successful"] += 1

                    except Exception as e:
                        logger.error(f"Error processing {image_path}: {e}")
                        batch_data["errors"].append({
                            "index": idx,
                            "image_path": image_path,
                            "error": str(e)
                        })
                        batch_data["failed"] += 1

                    finally:
                        batch_data["processed"] += 1

                        # Call progress callback
                        if progress_callback:
                            await progress_callback(batch_data)

            # Execute all tasks
            tasks = [
                process_with_semaphore(idx, path)
                for idx, path in enumerate(image_paths)
            ]

            await asyncio.gather(*tasks)

            # Finalize batch
            batch_data["end_time"] = datetime.utcnow().isoformat()
            batch_data["status"] = "completed"

            return batch_data

        finally:
            # SECURITY: Clean up batch directory to prevent disk space leaks
            if cleanup_files and batch_dir and batch_dir.exists():
                try:
                    shutil.rmtree(batch_dir)
                    logger.info(f"Cleaned up batch directory: {batch_dir}")
                except Exception as cleanup_error:
                    logger.error(f"Failed to cleanup batch directory {batch_dir}: {cleanup_error}")

    def get_batch_status(self, batch_id: str) -> Optional[Dict]:
        """Get current status of a batch.

        Args:
            batch_id: Batch identifier

        Returns:
            Batch status dictionary or None
        """
        return self.active_batches.get(batch_id)

    def export_batch_results(
        self,
        batch_id: str,
        output_format: str = "json"
    ) -> Optional[str]:
        """Export batch results to file.

        Args:
            batch_id: Batch identifier
            output_format: Output format (json, csv)

        Returns:
            Path to exported file or None
        """
        batch_data = self.active_batches.get(batch_id)
        if not batch_data:
            return None

        output_dir = Path("batch_results")
        output_dir.mkdir(exist_ok=True)

        if output_format == "json":
            output_path = output_dir / f"batch_{batch_id}.json"
            with open(output_path, 'w') as f:
                json.dump(batch_data, f, indent=2)

        elif output_format == "csv":
            output_path = output_dir / f"batch_{batch_id}.csv"
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)

                # Write header
                writer.writerow([
                    "Index", "Image Path", "Success",
                    "Alt Text", "SEO Score",
                    "Instagram Caption", "Engagement Score",
                    "SEO Title", "SEO Filename"
                ])

                # Write results
                for result in batch_data["results"]:
                    if result["success"]:
                        data = result["data"]
                        alt_text = data.get("alt_text", {})
                        social = data.get("social_captions", {})
                        seo = data.get("seo_metadata", {})

                        writer.writerow([
                            result["index"],
                            result["image_path"],
                            "Yes",
                            alt_text.get("standard", ""),
                            alt_text.get("seo_score", ""),
                            social.get("instagram", {}).get("caption", ""),
                            social.get("instagram", {}).get("engagement_score", ""),
                            seo.get("title", ""),
                            seo.get("filename", "")
                        ])

                # Write errors
                for error in batch_data["errors"]:
                    writer.writerow([
                        error["index"],
                        error["image_path"],
                        "No",
                        error["error"],
                        "", "", "", "", ""
                    ])

        return str(output_path)


class ProgressTracker:
    """Track and report progress for batch operations."""

    def __init__(self):
        """Initialize progress tracker."""
        self.progress_data = {}

    def create_tracker(self, batch_id: str, total_items: int) -> None:
        """Create a new progress tracker.

        Args:
            batch_id: Batch identifier
            total_items: Total number of items to process
        """
        self.progress_data[batch_id] = {
            "total": total_items,
            "processed": 0,
            "percentage": 0.0,
            "start_time": datetime.utcnow(),
            "estimated_completion": None
        }

    def update(self, batch_id: str, processed_count: int) -> Dict:
        """Update progress.

        Args:
            batch_id: Batch identifier
            processed_count: Number of items processed

        Returns:
            Progress data dictionary
        """
        if batch_id not in self.progress_data:
            return {}

        tracker = self.progress_data[batch_id]
        tracker["processed"] = processed_count
        tracker["percentage"] = (processed_count / tracker["total"]) * 100

        # Calculate estimated completion
        if processed_count > 0:
            elapsed = (datetime.utcnow() - tracker["start_time"]).total_seconds()
            rate = processed_count / elapsed
            remaining = tracker["total"] - processed_count
            estimated_seconds = remaining / rate if rate > 0 else 0
            tracker["estimated_completion"] = f"{int(estimated_seconds)}s"

        return tracker

    def get_progress(self, batch_id: str) -> Optional[Dict]:
        """Get current progress.

        Args:
            batch_id: Batch identifier

        Returns:
            Progress dictionary or None
        """
        return self.progress_data.get(batch_id)
