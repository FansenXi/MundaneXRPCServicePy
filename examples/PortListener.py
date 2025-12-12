import socket

# Ensure MSG_WAITALL constant is available
if not hasattr(socket, 'MSG_WAITALL'):
    socket.MSG_WAITALL = 0
import struct
import datetime
import os
import subprocess
import collections

# Import SDK
import xrobotoolkit_sdk as xrt

# Server configuration
HOST = '0.0.0.0'  # Listen on all network interfaces
PORT = 12345      # Listening port 12345
BUFFER_SIZE = 65536  # Receive buffer size

# Performance optimization configuration
PRINT_INTERVAL = 10  # Print log every N frames
FLUSH_INTERVAL = 10  # Flush file every N frames (only effective when SAVE_VIDEO=True)

# Video file saving configuration
SAVE_VIDEO = FALSE  # Whether to save video data to file (default: False)
VIDEO_OUTPUT_DIR = "video_output"
VIDEO_FILE_PREFIX = "received_video"

# Memory buffer configuration
USE_MEMORY_BUFFER = True  # Whether to use memory buffer to store video frames
MAX_BUFFER_SIZE = 100  # Maximum number of frames in memory buffer (to prevent memory overflow)
video_buffer = collections.deque(maxlen=MAX_BUFFER_SIZE)  # Video frame buffer, each element is a (timestamp, frame_data) tuple



def main():
    """
    Main function, initialize SDK and start TCP server
    """
    # Initialize SDK
    print("Initializing SDK...")
    try:
        xrt.init()
        print("SDK initialized successfully")
    except Exception as e:
        print(f"Failed to initialize SDK: {e}")
        return
    
    # Create TCP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Set receive buffer size
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
    
    # Bind to specified host and port
    s.bind((HOST, PORT))
    
    # Start listening, allowing up to 5 pending connections
    s.listen(5)
    
    print(f"TCP server is listening on {HOST}:{PORT}...")
    
    # Create directory for saving videos
    if SAVE_VIDEO and not os.path.exists(VIDEO_OUTPUT_DIR):
        os.makedirs(VIDEO_OUTPUT_DIR)
        print(f"Created video output directory: {VIDEO_OUTPUT_DIR}")
    
    # Create video file (if needed)
    video_file = None
    if SAVE_VIDEO:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        video_file_path = os.path.join(VIDEO_OUTPUT_DIR, f"{VIDEO_FILE_PREFIX}_{timestamp}.h265")
        video_file = open(video_file_path, "wb")
        print(f"Video data will be saved to: {video_file_path}")
    
    total_packets = 0
    total_video_data_size = 0
    
    # FPS calculation variables
    frame_timestamps = []
    fps_calculation_interval = 1.0  # Calculate FPS every second
    
    try:
        while True:
            try:
                print("Waiting for client connection...")
                conn, addr = s.accept()
                print(f"Client connected: {addr}")
                
                # Handle single client connection
                while True:
                    # First receive 4-byte length header
                    header = conn.recv(4)
                    if not header:
                        print(f"Client {addr} disconnected")
                        break
                        
                    # Parse length header (big-endian)
                    video_data_length = struct.unpack('>I', header)[0]  # > indicates big-endian, I indicates unsigned integer
                    
                    if video_data_length <= 0:
                        print(f"Invalid video data length from {addr}: {video_data_length}")
                        continue
                    
                    # Receive complete video data
                    try:
                        # Use MSG_WAITALL to try to receive all data at once for efficiency
                        received_data = conn.recv(video_data_length, socket.MSG_WAITALL)
                        if len(received_data) != video_data_length:
                            print(f"Client {addr} disconnected, incomplete data received")
                            break
                    except socket.error as e:
                        # Fall back to loop receive if MSG_WAITALL fails
                        received_data = b''
                        remaining = video_data_length
                        
                        while remaining > 0:
                            chunk = conn.recv(min(remaining, BUFFER_SIZE))
                            if not chunk:
                                print(f"Client {addr} disconnected")
                                break
                            received_data += chunk
                            remaining -= len(chunk)
                        
                        if remaining > 0:
                            print(f"Client {addr} disconnected while receiving video data")
                            break
                    
                    total_packets += 1
                    packet_size = len(received_data)
                    total_video_data_size += packet_size
                    
                    # Print reception information (print every N packets to avoid excessive output)
                    if total_packets % PRINT_INTERVAL == 0:
                        print(f"\nReception Statistics:")
                        print(f"  Total packets: {total_packets}")
                        print(f"  Current packet size: {packet_size} bytes")
                        print(f"  Video data length: {video_data_length} bytes")
                        print(f"  Total video data: {total_video_data_size} bytes ({total_video_data_size / (1024 * 1024):.2f} MB)")
                        print(f"  Source: {addr}")
                    
                    # Write video data to file
                    if video_file:
                        video_file.write(received_data)
                        # Flush every N frames to balance performance and data integrity
                        if total_packets % FLUSH_INTERVAL == 0:
                            video_file.flush()  # Ensure data is written to file
                    
                    # Add video data to memory buffer
                    if USE_MEMORY_BUFFER:
                        timestamp = datetime.datetime.now()
                        video_buffer.append((timestamp, received_data))
                        
                        # FPS calculation
                        frame_timestamps.append(timestamp)
                        
                        # Remove timestamps older than the calculation interval
                        current_time = datetime.datetime.now()
                        cutoff_time = current_time - datetime.timedelta(seconds=fps_calculation_interval)
                        frame_timestamps = [ts for ts in frame_timestamps if ts >= cutoff_time]
                        
                        # Print buffer status and FPS every N frames
                        if total_packets % PRINT_INTERVAL == 0:
                            print(f"Memory buffer status: {len(video_buffer)}/{MAX_BUFFER_SIZE} frames")
                            # Calculate and print FPS
                            if frame_timestamps:
                                fps = len(frame_timestamps) / fps_calculation_interval
                                print(f"Current FPS: {fps:.2f} FPS")
                    
                    # Output video stream data (print every N frames)
                    if total_packets % PRINT_INTERVAL == 0:
                        print(f"Received video data: length={len(received_data)} bytes")
                    # Video data processing logic can be added here
                    # Example: Print hexadecimal representation of first 10 bytes
                    # print(f"Data header: {received_data[:10].hex()}")
                
                # Close client connection
                conn.close()
                
            except KeyboardInterrupt:
                print("\nServer is shutting down...")
                break
            except Exception as e:
                print(f"Error processing data: {e}")
                continue
        
    finally:
        # Close video file (if open)
        if video_file:
            video_file.close()
            print("Video file closed")
        
        # Close server socket
        s.close()
        print("TCP server closed")
        
        # Close SDK
        print("Shutting down SDK...")
        try:
            xrt.close()
            print("SDK closed")
        except Exception as e:
            print(f"Error shutting down SDK: {e}")
    
    # Final Statistics
    print(f"\nFinal Statistics:")
    print(f"  Total packets: {total_packets}")
    print(f"  Total video data: {total_video_data_size} bytes ({total_video_data_size / (1024 * 1024):.2f} MB)")


if __name__ == "__main__":
    print("=== PortListener - Video Stream Receiver Server ===")
    print("Press Ctrl+C to stop")
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"Error running program: {e}")
        import traceback
        traceback.print_exc()