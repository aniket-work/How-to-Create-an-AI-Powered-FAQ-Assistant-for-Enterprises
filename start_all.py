#!/usr/bin/env python3
"""
Script to start both the backend and frontend servers for the Enterprise FAQ Assistant.
"""
import subprocess
import sys
import time
import threading

def print_status(message):
    """Print status messages with a consistent format."""
    print(f"[INFO] {message}")

def start_backend():
    """Start the backend server."""
    print_status("Starting backend server...")
    try:
        # Start the backend server
        backend_process = subprocess.Popen([
            sys.executable, "start_backend.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a moment for the server to start
        time.sleep(2)
        
        # Check if the process is still running
        if backend_process.poll() is None:
            print_status("Backend server started successfully on http://localhost:8001")
            return backend_process
        else:
            stdout, stderr = backend_process.communicate()
            print(f"[ERROR] Backend failed to start: {stderr}")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the frontend server."""
    print_status("Starting frontend server...")
    try:
        # Start the frontend server
        frontend_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "app.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a moment for the server to start
        time.sleep(3)
        
        # Check if the process is still running
        if frontend_process.poll() is None:
            print_status("Frontend server started successfully on http://localhost:8503")
            return frontend_process
        else:
            stdout, stderr = frontend_process.communicate()
            print(f"[ERROR] Frontend failed to start: {stderr}")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to start frontend: {e}")
        return None

def monitor_processes(backend_process, frontend_process):
    """Monitor both processes and restart if needed."""
    try:
        while True:
            time.sleep(1)
            
            # Check backend
            if backend_process and backend_process.poll() is not None:
                print("[WARNING] Backend process has stopped. Restarting...")
                backend_process = start_backend()
            
            # Check frontend
            if frontend_process and frontend_process.poll() is not None:
                print("[WARNING] Frontend process has stopped. Restarting...")
                frontend_process = start_frontend()
                
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down servers...")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        sys.exit(0)

def main():
    """Main function to start both servers."""
    print_status("Starting Enterprise FAQ Assistant Platform")
    print_status("========================================")
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("[ERROR] Failed to start backend. Exiting.")
        sys.exit(1)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("[ERROR] Failed to start frontend. Exiting.")
        if backend_process:
            backend_process.terminate()
        sys.exit(1)
    
    print_status("Both servers are running!")
    print_status("Backend:  http://localhost:8001")
    print_status("Frontend: http://localhost:8503")
    print_status("Press Ctrl+C to stop both servers")
    print_status("========================================")
    
    # Monitor both processes
    monitor_processes(backend_process, frontend_process)

if __name__ == "__main__":
    main()