import speedtest
import socket
import requests
import sqlite3
import os
import time
from datetime import datetime
from plyer import notification

DB_NAME = "speed_history.db"


# DATABASE SETUP

def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS speeds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            download REAL,
            upload REAL,
            ping REAL
        )
    """)
    conn.commit()
    conn.close()


def save_results(download, upload, ping):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO speeds (timestamp, download, upload, ping)
        VALUES (?, ?, ?, ?)
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), download, upload, ping))
    conn.commit()
    conn.close()


def get_last_result():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT download, upload, ping FROM speeds ORDER BY id DESC LIMIT 1 OFFSET 1")
    result = cursor.fetchone()
    conn.close()
    return result



# INTERNET SPEED TEST

def test_speed():
    print("Testing internet speed... Please wait...\n")
    st = speedtest.Speedtest()

    st.get_best_server()
    download = st.download() / 1_000_000
    upload = st.upload() / 1_000_000
    ping = st.results.ping

    return round(download, 2), round(upload, 2), round(ping, 2)



# GET PUBLIC IP INFO
def get_ip_info():
    try:
        response = requests.get("https://api.ipify.org?format=json")
        ip = response.json()["ip"]
        return ip
    except:
        return "Unavailable"
    
    
def view_history():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM speeds ORDER BY id DESC")
    rows = cursor.fetchall()

    print("\n===== SPEED TEST HISTORY =====\n")

    if not rows:
        print("No data found.")
    else:
        for row in rows:
            print(f"""
ID: {row[0]}
Time: {row[1]}
Download: {row[2]} Mbps
Upload: {row[3]} Mbps
Ping: {row[4]} ms
---------------------------
""")

    conn.close()



# OPTIMIZATION SUGGESTIONS

def optimization_tips(download, ping):
    print("\n--- Optimization Suggestions ---")

    if download < 10:
        print("• Your speed is low. Try restarting your router.")
        print("• Move closer to Wi-Fi router.")
        print("• Upgrade your ISP plan.")
    elif ping > 100:
        print("• High ping detected.")
        print("• Use Ethernet instead of Wi-Fi.")
        print("• Close background downloads.")
    else:
        print("• Your connection looks healthy!")

# MAIN PROGRAM

def main():
    create_database()

    print("===== INTERNET SPEED OPTIMIZER =====\n")

    ip = get_ip_info()
    print(f"Your Public IP: {ip}\n")

    download, upload, ping = test_speed()

    print("----- Current Results -----")
    print(f"Download Speed: {download} Mbps")
    print(f"Upload Speed:   {upload} Mbps")
    print(f"Ping:           {ping} ms")

    save_results(download, upload, ping)

    last = get_last_result()

    if last:
        print("\n----- Comparison With Previous Test -----")
        print(f"Previous Download: {last[0]} Mbps")
        print(f"Previous Upload:   {last[1]} Mbps")
        print(f"Previous Ping:     {last[2]} ms")

    optimization_tips(download, ping)

    notification.notify(
        title="Speed Test Completed",
        message=f"Download: {download} Mbps | Ping: {ping} ms",
        timeout=5
    )
    
    print("===== INTERNET SPEED ANALYZER =====")
    print("1. Run Speed Test")
    print("2. View History")
    print("3. Exit")

    choice = input("\nSelect an option: ")

    if choice == "1":
        ip = get_ip_info()
        print("\nPublic IP:", ip)

        download, upload, ping = test_speed()

        if download is None:
            return

        print("\n----- Current Results -----")
        print("Download:", download, "Mbps")
        print("Upload:  ", upload, "Mbps")
        print("Ping:    ", ping, "ms")

        save_results(download, upload, ping)

        optimization_tips(download, ping)

    elif choice == "2":
        view_history()

    elif choice == "3":
        print("Exiting program...")

    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()