import requests
import time
import json
import urllib3
import hmac
import random
import hashlib
import string
from typing import Optional, Dict, Any

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Konstanta global
BASE_URL = "https://wonton.food"
HEADERS = {
    "Host": "wonton.food",
    "content-type": "application/json",
    "accept": "*/*",
    "sec-fetch-site": "cross-site",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "sec-fetch-mode": "cors",
    "origin": "https://www.wonton.restaurant",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "referer": "https://www.wonton.restaurant/",
    "sec-fetch-dest": "empty",
}

def tampilkan_logo():
    logo = r"""
  _____ _____ _____      _    _         _                 
 |___  |___  |___  |    / \  (_)_ __ __| |_ __ ___  _ __  
    / /   / /   / /    / _ \ | | '__/ _` | '__/ _ \| '_ \ 
   / /   / /   / /    / ___ \| | | | (_| | | | (_) | |_) |
  /_/   /_/   /_/    /_/   \_\_|_|  \__,_|_|  \___/| .__/ 
                                                   |_|          
    Channel : https://t.me/sevensevensevenairdrop
    """
    print(logo)

def baca_init_data() -> Optional[list]:
    try:
        with open("wonton.txt", "r") as file:
            return file.readlines()
    except FileNotFoundError:
        print("Error: File wonton.txt not found.")
    except IOError:
        print("Error: error read file wonton.txt.")
    return None

def generate_x_tag() -> str:
    secret_key = "wonton.food"
    timestamp = int(time.time() * 1000)
    nonce = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    message = f"{timestamp}:{nonce}"
    signature = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()
    return f"{timestamp}:{nonce}:{signature}"

def make_request(method: str, endpoint: str, auth_token: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    url = f"{BASE_URL}{endpoint}"
    headers = HEADERS.copy()
    headers["x-tag"] = generate_x_tag()
    
    if auth_token:
        headers["authorization"] = f"bearer {auth_token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, verify=False)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, verify=False)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error during {method} request to {endpoint}: {e}")
    return None

def autentikasi_pengguna(init_data: str, invite_code: Optional[str] = None) -> Optional[Dict[str, Any]]:
    data = {"initData": init_data, "inviteCode": invite_code, "newUserPromoteCode": ""}
    return make_request("POST", "/api/v1/user/auth", data=data)

def get_farming_status(auth_token: str) -> Optional[Dict[str, Any]]:
    return make_request("GET", "/api/v1/user/farming-status", auth_token)

def start_farming(auth_token: str) -> Optional[Dict[str, Any]]:
    return make_request("POST", "/api/v1/user/start-farming", auth_token)

def start_game(auth_token: str) -> Optional[Dict[str, Any]]:
    return make_request("POST", "/api/v1/user/start-game", auth_token)

def finish_game(auth_token: str, points: int, has_bonus: bool) -> Optional[Dict[str, Any]]:
    data = {"points": points, "hasBonus": has_bonus}
    return make_request("POST", "/api/v1/user/finish-game", auth_token, data)

def claim_gift(auth_token: str) -> Optional[Dict[str, Any]]:
    result = make_request("POST", "/api/v1/user/farming-claim", auth_token)
    if result:
        print(f"Farming response: {result}")
    return result

def process_user(init_data: str, invite_code: Optional[str]):
    response_data = autentikasi_pengguna(init_data.strip(), invite_code)
    if not response_data or "user" not in response_data or "id" not in response_data["user"]:
        print("Error: initData error. Response does not contain user ID.")
        return

    user = response_data["user"]
    print(f"Halo {user['firstName']} - Balance {user['tokenBalance']} - Ticket {response_data['ticketCount']}")

    if "tokens" not in response_data:
        print("Token not found in authentication response.")
        return

    auth_token = response_data["tokens"]["accessToken"]

    # Farming
    farming_status = claim_gift(auth_token)
    if farming_status:
        if not farming_status["claimed"]:
            print("Status Farming")
        else:
            print("Claim farming")
            start_farming(auth_token)

    # Game
    while int(response_data["ticketCount"]) > 0:
        print(f"Remaining tickets: {response_data['ticketCount']}")
        print("Starting the game...")
        if start_game(auth_token):
            print("Let's start this game. Waiting 15 seconds...")
            time.sleep(15)
            points = random.randint(300, 500)
            has_bonus = False
            print("Finishing the game...")
            if finish_game(auth_token, points, has_bonus):
                print(f"The game is finished by getting points {points}.")
                response_data["ticketCount"] = str(int(response_data["ticketCount"]) - 1)
            else:
                print("Failed to complete the game. Try again...")
                continue
        else:
            print("Failed to start the game. Try again...")
            continue

        time.sleep(random.randint(5, 8))

    print("Ticket allready used.")

def main():
    tampilkan_logo()
    invite_code = input("Enter your referral code (enter if not needed) : ")

    while True:
        init_data_list = baca_init_data()
        if not init_data_list:
            print("No valid init data. The program stops.")
            return

        for init_data in init_data_list:
            process_user(init_data, invite_code)
            time.sleep(5)

        print("\nAll initData has been processed. Starting over from the beginning...")
        time.sleep(10800)

if __name__ == "__main__":
    main()
