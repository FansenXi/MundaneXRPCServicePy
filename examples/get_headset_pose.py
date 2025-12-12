import sys
import time
import math

import xrobotoolkit_sdk as xrt


def quaternion_to_euler(qx, qy, qz, qw):
    """
    将四元数转换为欧拉角（Yaw, Pitch, Roll）
    返回角度（度）
    """
    # 计算偏航角 (yaw) - Z轴旋转
    siny_cosp = 2 * (qw * qz + qx * qy)
    cosy_cosp = 1 - 2 * (qy * qy + qz * qz)
    yaw = math.atan2(siny_cosp, cosy_cosp)
    
    # 计算俯仰角 (pitch) - Y轴旋转
    sinp = 2 * (qw * qy - qz * qx)
    if abs(sinp) >= 1:
        pitch = math.copysign(math.pi / 2, sinp)  # 避免数值不稳定
    else:
        pitch = math.asin(sinp)
    
    # 计算滚转角 (roll) - X轴旋转
    sinr_cosp = 2 * (qw * qx + qy * qz)
    cosr_cosp = 1 - 2 * (qx * qx + qy * qy)
    roll = math.atan2(sinr_cosp, cosr_cosp)
    
    # 转换为角度
    yaw_deg = math.degrees(yaw)
    pitch_deg = math.degrees(pitch)
    roll_deg = math.degrees(roll)
    
    return yaw_deg, pitch_deg, roll_deg


def get_headset_quaternion_60hz():
    """
    以60Hz频率获取并输出头部姿势的四元数返回值的函数
    """
    print("Starting Headset Quaternion Collection at 60Hz...")

    try:
        print("Initializing SDK...")
        xrt.init()
        print("SDK Initialized successfully.")

        print(f"\n--- Outputting Headset Quaternion at 60Hz ---")
        print("Press Ctrl+C to stop.")
        
        iteration = 1
        target_frequency = 60
        target_interval = 1.0 / target_frequency
        collected_samples = 0
        
        print("Waiting for valid data...")
        
        # 先等待获取到有效数据
        while True:
            # 记录当前迭代开始时间
            iteration_start = time.time()
            
            # 获取头部姿势
            headset_pose = xrt.get_headset_pose()
            
            # 获取时间戳
            timestamp = xrt.get_time_stamp_ns()
            
            # 检查数据是否有效（时间戳不为0）
            if timestamp != 0:
                break

            elapsed = time.time() - iteration_start
            sleep_time = max(0, target_interval - elapsed)
            time.sleep(sleep_time)
            iteration += 1
        
        print("Valid data received, starting output...")
        
        # 持续输出四元数数据
        while True:
            # 记录当前迭代开始时间
            iteration_start = time.time()
            
            # 获取头部姿势
            headset_pose = xrt.get_headset_pose()
            
            # 解析四元数 (qw, qx, qy, qz)
            qx, qy, qz, qw = headset_pose[3], headset_pose[4], headset_pose[5], headset_pose[6]
            
            # 组合成四元数返回值
            quaternion = (qw, qx, qy, qz)  # 标准四元数格式 (qw, qx, qy, qz)
            
            # 输出四元数
            print(f"Quaternion: {quaternion}")
            
            collected_samples += 1
            
            # 计算应该睡眠的时间，以保持60Hz的频率
            elapsed = time.time() - iteration_start
            sleep_time = max(0, target_interval - elapsed)
            time.sleep(sleep_time)
            
            return quaternion

    except KeyboardInterrupt:
        print(f"\n\nData collection stopped by user.")
        print(f"Total samples collected: {collected_samples}")
    except RuntimeError as e:
        print(f"Runtime Error: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
    finally:
        print("\nClosing SDK...")
        xrt.close()
        print("SDK closed.")
        print("Headset quaternion collection finished.")


if __name__ == "__main__":
    get_headset_quaternion_60hz()