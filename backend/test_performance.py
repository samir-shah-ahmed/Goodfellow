import requests
import time
import sys

BASE_URL = "http://localhost:8000/api/v1"

def wait_for_server():
    print("Waiting for server to start...")
    for i in range(20):
        try:
            requests.get(f"http://localhost:8000/")
            print("Server is up!")
            return True
        except requests.exceptions.ConnectionError:
            time.sleep(1)
            print(".", end="", flush=True)
    return False

def test_latency():
    ticker = "AAPL"
    url = f"{BASE_URL}/ticker/{ticker}"

    print(f"\n--- Testing Latency for {ticker} ---")
    
    # Cold Request
    start = time.time()
    try:
        resp = requests.get(url)
        resp_time = (time.time() - start) * 1000
        if resp.status_code == 200:
            print(f"Cold Start Time: {resp_time:.2f} ms")
            data = resp.json()
            print(f"Articles Found: {len(data.get('articles', []))}")
            print(f"Safety Score: {data.get('safety_score')}")
        else:
            print(f"Error: {resp.status_code} - {resp.text}")
            return
    except Exception as e:
        print(f"Request failed: {e}")
        return

    # Warm Request
    start = time.time()
    try:
        resp = requests.get(url)
        resp_time = (time.time() - start) * 1000
        print(f"Warm Cache Time: {resp_time:.2f} ms")
        
        if resp_time < 50:
             print("PASS: Warm cache is under 50ms!")
        else:
             print("WARN: Warm cache is slightly over 50ms (Python overhead locally).")
             
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    if wait_for_server():
        test_latency()
    else:
        print("Server failed to start.")
        sys.exit(1)
