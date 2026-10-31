#!/usr/bin/env python3
import subprocess

def get_vm_stats():
    print("=== VM Resource Profiler ===")
    try:
        load_output = subprocess.check_output(["uptime"]).decode('utf-8').strip()
        print(f"System Load: {load_output}")
        
        mem_output = subprocess.check_output(["free", "-m"]).decode('utf-8').strip()
        mem_lines = mem_output.split('\n')
        mem_parts = mem_lines[1].split()
        
        total_mem = int(mem_parts[1])
        used_mem = int(mem_parts[2])
        usage_pct = (used_mem / total_mem) * 100
        
        print(f"Total VM RAM: {total_mem} MB")
        print(f"Used VM RAM: {used_mem} MB ({usage_pct:.1f}%)")
        
        if usage_pct > 90:
            print("[WARN] Memory pressure is HIGH. Consider increasing 'vmc resize'.")
        elif usage_pct < 20:
            print("[INFO] VM is underutilizing allocated RAM.")
        else:
            print("[PASS] Memory utilization is within healthy bounds.")
    except Exception as e:
        print(f"[ERROR] Resource profiling failed: {e}")

if __name__ == "__main__":
    get_vm_stats()
