#!/usr/bin/env python3
"""
entropy_core.py — Algorithmic Entropy Distillation

Transforms video frame differences into cryptographic-quality random numbers.
Uses frame differencing, thresholding, bit extraction, and SHA-256 hashing.

Inspired by Cloudflare's LavaRand — capturing thermodynamic chaos optically.

Usage:
    # Process a pre-recorded video
    python entropy_core.py --input capture.mp4 --output entropy_seed.txt

    # Process a directory of frame images
    python entropy_core.py --frames ./captured_frames/ --output entropy_seed.txt

    # Live camera mode
    python entropy_core.py --live --output entropy_seed.txt

    # Raw binary output for statistical testing
    python entropy_core.py --live --output entropy.bin --raw

Dependencies:
    pip install opencv-python numpy
"""

import argparse
import hashlib
import os
import sys
import time
from pathlib import Path

import cv2
import numpy as np


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DEFAULT_THRESHOLD = 15      # Pixel difference threshold (filter camera noise)
BYTE_BLOCK_SIZE = 8         # Bits per entropy block
READ_BUFFER_SIZE = 500      # Frames to buffer before hashing
SHA256_DIGEST_BYTES = 32    # 256 bits


# ---------------------------------------------------------------------------
# Core Entropy Extraction
# ---------------------------------------------------------------------------

class EntropyExtractor:
    """
    Core entropy extraction engine.
    Converts frame-to-frame pixel changes into SHA-256 hashed output.
    """

    def __init__(self, threshold: int = DEFAULT_THRESHOLD):
        self.threshold = threshold
        self.prev_frame = None
        self.bit_buffer = []
        self.byte_buffer = bytearray()
        self.block_count = 0
        self.total_changes = 0
        self.frame_count = 0

    def process_frame(self, frame: np.ndarray) -> bytes:
        """
        Process a single grayscale frame.
        Returns a SHA-256 digest when enough entropy has been accumulated,
        or None otherwise.
        """
        if frame.ndim == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        self.frame_count += 1

        if self.prev_frame is None:
            self.prev_frame = frame
            return None

        # Stage 1: Frame differencing
        diff = cv2.absdiff(self.prev_frame, frame)

        # Stage 2: Binary threshold
        _, binary = cv2.threshold(diff, self.threshold, 255, cv2.THRESH_BINARY)

        # Stage 3: Count changed pixels
        changed_pixels = np.count_nonzero(binary)
        total_pixels = binary.shape[0] * binary.shape[1]
        self.total_changes += changed_pixels

        # Normalize change count to 0.0 - 1.0
        change_ratio = changed_pixels / total_pixels if total_pixels > 0 else 0.0

        # Extract entropy bits from the change ratio
        self._extract_bits(change_ratio)

        # Update previous frame
        self.prev_frame = frame

        # If buffer is full, hash and return
        if len(self.byte_buffer) >= READ_BUFFER_SIZE:
            return self._flush_buffer()

        return None

    def _extract_bits(self, change_ratio: float):
        """Extract multiple bits from the change ratio for better entropy density."""
        # Scale to 0-255 range
        scaled = int(change_ratio * 255)

        # Extract 3 least significant bits (most entropic)
        for bit_pos in range(3):
            bit = (scaled >> bit_pos) & 1
            self.bit_buffer.append(bit)

            # Assemble 8-bit blocks
            if len(self.bit_buffer) >= BYTE_BLOCK_SIZE:
                byte_val = 0
                for b in self.bit_buffer[:BYTE_BLOCK_SIZE]:
                    byte_val = (byte_val << 1) | b
                self.byte_buffer.append(byte_val)
                self.bit_buffer = self.bit_buffer[BYTE_BLOCK_SIZE:]

    def _flush_buffer(self) -> bytes:
        """Hash the accumulated entropy buffer and return the digest."""
        if not self.byte_buffer:
            return None

        raw_bytes = bytes(self.byte_buffer)
        digest = hashlib.sha256(raw_bytes).digest()

        self.block_count += 1
        self.byte_buffer = bytearray()

        return digest

    def get_stats(self) -> dict:
        """Return current extraction statistics."""
        return {
            "frames_processed": self.frame_count,
            "total_pixel_changes": self.total_changes,
            "blocks_generated": self.block_count,
            "buffer_pending": len(self.byte_buffer),
        }


# ---------------------------------------------------------------------------
# Input Sources
# ---------------------------------------------------------------------------

def process_video_file(video_path: str, extractor: EntropyExtractor):
    """Process frames from a video file."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"ERROR: Could not open video: {video_path}", file=sys.stderr)
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Processing video: {video_path} ({total_frames} frames)")

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        digest = extractor.process_frame(frame)
        if digest:
            yield f"BLOCK {extractor.block_count:04d}: {digest.hex()}"

        frame_idx += 1
        if frame_idx % 100 == 0:
            print(f"  Progress: {frame_idx}/{total_frames} frames")

    cap.release()


def process_frame_directory(dir_path: str, extractor: EntropyExtractor):
    """Process frames from a directory of images (sorted by filename)."""
    image_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".tiff"}
    frames = sorted(
        [f for f in Path(dir_path).iterdir() if f.suffix.lower() in image_extensions]
    )

    if not frames:
        print(f"ERROR: No image files found in: {dir_path}", file=sys.stderr)
        return

    print(f"Processing {len(frames)} frames from: {dir_path}")

    for i, frame_path in enumerate(frames):
        frame = cv2.imread(str(frame_path), cv2.IMREAD_GRAYSCALE)
        if frame is None:
            print(f"WARNING: Could not read: {frame_path}", file=sys.stderr)
            continue

        digest = extractor.process_frame(frame)
        if digest:
            yield f"BLOCK {extractor.block_count:04d}: {digest.hex()}"

        if (i + 1) % 100 == 0:
            print(f"  Progress: {i+1}/{len(frames)} frames")


def process_live_camera(extractor: EntropyExtractor, camera_id: int = 0):
    """Process frames live from a camera."""
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        print(f"ERROR: Could not open camera (index {camera_id})", file=sys.stderr)
        return

    print("Live camera entropy extraction running. Press Ctrl+C to stop.\n")

    # Burn-in frames
    for _ in range(10):
        cap.read()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("WARNING: Frame read failed, retrying...", file=sys.stderr)
                time.sleep(0.1)
                continue

            digest = extractor.process_frame(frame)
            if digest:
                yield f"BLOCK {extractor.block_count:04d}: {digest.hex()}"

    except KeyboardInterrupt:
        print("\n\nLive capture stopped by user.")
    finally:
        cap.release()


# ---------------------------------------------------------------------------
# Output Handling
# ---------------------------------------------------------------------------

def write_output(output_stream, output_path: str, raw_mode: bool = False):
    """Write entropy output to stdout and optionally to a file."""
    file_handle = None
    if output_path:
        mode = "wb" if raw_mode else "w"
        file_handle = open(output_path, mode)
        print(f"Output written to: {output_path}")

    try:
        for line in output_stream:
            if raw_mode:
                # In raw mode, output is bytes from process_frame
                sys.stdout.buffer.write(line)
                if file_handle:
                    file_handle.write(line)
            else:
                print(line)
                if file_handle:
                    file_handle.write(line + "\n")

            # Flush periodically for real-time output
            if file_handle:
                file_handle.flush()
    finally:
        if file_handle:
            file_handle.close()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract cryptographic-quality entropy from LED video frames."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--input", "-i",
        help="Path to input video file (.mp4, .avi, etc.)",
    )
    source.add_argument(
        "--frames", "-f",
        help="Directory containing frame images (PNG, JPG)",
    )
    source.add_argument(
        "--live", "-l",
        action="store_true",
        help="Capture from live camera (index 0)",
    )

    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output file path (stdout if not specified)",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Output raw binary bytes instead of hex strings",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=DEFAULT_THRESHOLD,
        help=f"Pixel diff threshold (default: {DEFAULT_THRESHOLD})",
    )
    parser.add_argument(
        "--camera-id",
        type=int,
        default=0,
        help="Camera device index for live mode (default: 0)",
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    print("=" * 55)
    print("  LED-Entropy Core — Algorithmic Entropy Distillation")
    print("  Frame Differential  SHA-256 Extraction")
    print("=" * 55)
    print()

    extractor = EntropyExtractor(threshold=args.threshold)

    # Select source
    if args.input:
        stream = process_video_file(args.input, extractor)
    elif args.frames:
        stream = process_frame_directory(args.frames, extractor)
    elif args.live:
        stream = process_live_camera(extractor, args.camera_id)
    else:
        print("ERROR: No input source specified.", file=sys.stderr)
        sys.exit(1)

    # Write output
    write_output(stream, args.output, raw_mode=args.raw)

    # Print final stats
    stats = extractor.get_stats()
    print()
    print("Extraction Complete:")
    print(f"  Frames processed:      {stats['frames_processed']}")
    print(f"  Total pixel changes:   {stats['total_pixel_changes']}")
    print(f"  SHA-256 blocks output: {stats['blocks_generated']}")
    print(f"  Buffer bytes pending:  {stats['buffer_pending']}")
    print()


if __name__ == "__main__":
    main()
