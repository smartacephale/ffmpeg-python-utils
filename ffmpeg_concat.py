import os
import subprocess
import re
import argparse

def concatenate_videos_with_ffmpeg(folder_path, output_path, format):
    # Get a list of all MP4 files in the folder
    video_files = [f for f in os.listdir(folder_path) if f.endswith(format)]
    video_files.sort()  # Sort files alphabetically (optional)

    # Create a temporary file to list the videos for concatenation
    list_file_path = os.path.join(folder_path, "videos_to_concat.txt")
    with open(list_file_path, "w") as list_file:
        for video_file in video_files:
            list_file.write(f"file '{video_file}'\n")

    # Run the ffmpeg command to concatenate the videos
    ffmpeg_command = [
        "ffmpeg",
        "-f", "concat",          # Use the concat demuxer
        "-safe", "0",           # Allow unsafe file paths
        "-i", list_file_path,   # Input file list
        "-c", "copy",           # Copy codec (no re-encoding)
        output_path             # Output file
    ]

    # Execute the ffmpeg command
    subprocess.run(ffmpeg_command, check=True)

    # Clean up the temporary list file
    os.remove(list_file_path)

    print(f"Videos concatenated successfully! Output saved to {output_path}")


def get_video_duration(video_path):
    """
    Get the duration of a video using ffmpeg.
    """
    # Run ffmpeg command to probe the video file
    command = [
        "ffmpeg",
        "-i", video_path
    ]
    result = subprocess.run(command, stderr=subprocess.PIPE, text=True)

    # Extract duration using regex
    duration_match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", result.stderr)
    if duration_match:
        hours = int(duration_match.group(1))
        minutes = int(duration_match.group(2))
        seconds = float(duration_match.group(3))
        total_seconds = hours * 3600 + minutes * 60 + seconds
        return total_seconds
    else:
        raise ValueError(f"Could not extract duration from {video_path}")

def calculate_total_duration(folder_path, format):
    """
    Calculate the total duration of all MP4 videos in a folder.
    """
    total_duration = 0.0

    # Get a list of all MP4 files in the folder
    video_files = [f for f in os.listdir(folder_path) if f.endswith(format)]

    # Calculate the total duration
    for video_file in video_files:
        video_path = os.path.join(folder_path, video_file)
        try:
            duration = get_video_duration(video_path)
            total_duration += duration
            print(f"Processed: {video_file} (Duration: {duration:.2f} seconds)")
        except Exception as e:
            print(f"Error processing {video_file}: {e}")

    return total_duration


if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Calculate the total duration of videos in a folder.")
    parser.add_argument("--path", type=str, default="./", help="Path to the folder containing the videos.")
    parser.add_argument("--output", type=str, default="./concat_video.mp4", help="Output path and file format.")
    parser.add_argument("--format", type=str, default=".mp4", help="File format of the videos (e.g., .mp4, .mkv). Default is .mp4.")
    args = parser.parse_args()

    # Calculate the total duration
    total_duration = calculate_total_duration(args.path, args.format)
    print(f"Total duration of all videos: {total_duration:.2f} seconds")

    # Call the function to concatenate videos
    concatenate_videos_with_ffmpeg(args.path, args.output, args.format)
