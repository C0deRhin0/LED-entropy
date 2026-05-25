#!/usr/bin/env python3
"""
camera_capture_engine.py — Raspberry Pi Camera Frame Capture

Captures grayscale video frames from a Pi Camera module at 30 fps.
Output: Individual frame files for entropy processing, plus a calibration frame.

Usage:
    python camera_capture_engine.py                     # Live capture to frames/
    python camera_capture_engine.py --output ./my_frames # Custom output directory
    python camera_capture_engine.py --duration 60        # Capture for 60 seconds
    python camera_capture_engine.py --fps 15             # Lower framerate

Dependencies:
    pip install opencv-python numpy
"""

import argparse
import os
import sys
import time
from datetime import datetime

import cv2
import numpy as np


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Capture grayscale frames from Pi Camera for entropy extraction."
    )
    parser.add_argument(
        "--output",
        "-o",
        default="./captured_frames",
        help="Directory to save captured frames (default: ./captured_frames)",
    )
    parser.add_argument(
        "--duration",
        "-d",
        type=int,
        default=0,
        help="Capture duration in seconds (0 = run until Ctrl+C)",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=30,
        help="Target frames per second (default: 30)",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=640,
        help="Capture width in pixels (default: 640)",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=480,
        help="Capture height in pixels (default: 480)",
    )
    parser.add_argument(
        "--calibration-only",
        action="store_true",
        help="Save a single calibration frame and exit",
    )
    return parser.parse_args()


def setup_camera(width: int, height: int, target_fps: int) -> cv2.VideoCapture:
    """Initialize the camera with specified parameters."""
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("ERROR: Could not open camera (index 0).", file=sys.stderr)
        print("Try: ls /dev/video* to verify camera detection.", file=sys.stderr)
        sys.exit(1)

    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, target_fps)

    # Read actual values (camera may not support exact request)
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = cap.get(cv2.CAP_PROP_FPS)

    print(f"Camera initialized: {actual_width}x{actual_height} @ {actual_fps:.1f} fps")
    return cap


def save_calibration_frame(cap: cv2.VideoCapture) -> str:
    """Capture and save a single calibration frame."""
    print("Capturing calibration frame...")

    # Warm up: discard first few frames for auto-exposure settling
    for _ in range(10):
        cap.read()

    ret, frame = cap.read()
    if not ret:
        print("ERROR: Failed to capture calibration frame.", file=sys.stderr)
        return ""

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    filename = "lens_calibration_proof.png"
    cv2.imwrite(filename, gray)
    print(f"Calibration frame saved: {filename}")
    print(f"  Dimensions: {gray.shape[1]}x{gray.shape[0]}")
    print(f"  Pixel range: {gray.min()} - {gray.max()}")
    print(f"  Mean value: {gray.mean():.1f}")
    return filename


def run_capture_loop(
    cap: cv2.VideoCapture,
    output_dir: str,
    duration: int,
    target_fps: int,
) -> int:
    """Main capture loop. Returns total frames saved."""
    os.makedirs(output_dir, exist_ok=True)

    frame_interval = 1.0 / target_fps
    saved_count = 0
    start_time = time.time()
    last_frame_time = 0

    print(f"\nCapturing frames to: {output_dir}/")
    print("Press Ctrl+C to stop early.\n")

    # Burn-in: allow auto-exposure and white balance to settle
    print("Warming up camera (10 frames)...")
    for _ in range(10):
        cap.read()

    try:
        while True:
            # Check duration limit
            if duration > 0 and (time.time() - start_time) > duration:
                print(f"\nDuration reached ({duration}s). Stopping capture.")
                break

            # Throttle to target fps
            now = time.time()
            if now - last_frame_time < frame_interval:
                time.sleep(0.001)  # Small yield to prevent busy-wait
                continue

            ret, frame = cap.read()
            if not ret:
                print("WARNING: Frame read failed, skipping...", file=sys.stderr)
                continue

            # Convert to grayscale immediately (color has no entropy value)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Save with timestamp-based filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = os.path.join(output_dir, f"frame_{timestamp}.png")
            cv2.imwrite(filename, gray)
            saved_count += 1
            last_frame_time = now

            # Show FPS every 30 frames
            if saved_count % 30 == 0:
                elapsed = time.time() - start_time
                fps = saved_count / elapsed if elapsed > 0 else 0
                print(
                    f"  Captured {saved_count} frames | "
                    f"Elapsed: {elapsed:.1f}s | "
                    f"Actual FPS: {fps:.1f}"
                )

    except KeyboardInterrupt:
        print("\n\nCapture stopped by user.")
    finally:
        elapsed = time.time() - start_time
        fps = saved_count / elapsed if elapsed > 0 else 0
        print(f"\nCapture Summary:")
        print(f"  Total frames:  {saved_count}")
        print(f"  Elapsed time:  {elapsed:.1f}s")
        print(f"  Average FPS:   {fps:.1f}")
        print(f"  Output dir:    {output_dir}/")

    return saved_count


def main():
    """Main entry point."""
    args = parse_args()

    print("=" * 50)
    print("  LED-Entropy Camera Capture Engine")
    print("  Optical Frame Acquisition")
    print("=" * 50)

    cap = setup_camera(args.width, args.height, args.fps)

    if args.calibration_only:
        save_calibration_frame(cap)
    else:
        # Save calibration frame first
        cal_file = save_calibration_frame(cap)
        if cal_file:
            # Then run live capture
            run_capture_loop(cap, args.output, args.duration, args.fps)
        else:
            print("ERROR: Calibration failed. Aborting capture.", file=sys.stderr)

    cap.release()
    print("\nCamera released. Capture session complete.")


if __name__ == "__main__":
    main()
