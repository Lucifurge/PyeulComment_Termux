import requests
import hashlib
import uuid
import random
import string
import time
import getpass
from rich import print as printf
from rich.panel import Panel
from rich.console import Console

console = Console()

banner = Panel(
    "[bold yellow]FACEBOOK AUTO COMMENT & TOKEN GENERATOR[/bold yellow]", 
    width=60, 
    title="[bold cyan]Auto Comment Bot[/bold cyan]", 
    border_style="blue",
    expand=False
)
console.print(banner)

def random_string(length=24):
    """Generate a random string of lowercase letters and numbers."""
    return ''.join(random.choices(string.ascii_lowercase + "0123456789", k=length))

def encode_sig(data):
    """Generate an MD5 signature for the request."""
    sorted_data = {k: data[k] for k in sorted(data)}
    data_str = ''.join(f"{key}={value}" for key, value in sorted_data.items())
    return hashlib.md5((data_str + '62f8ce9f74b12f84c123cc23437a4a32').encode()).hexdigest()

def generate_token(email, password):
    """Generate a Facebook access token securely."""
    device_id = str(uuid.uuid4())
    adid = str(uuid.uuid4())
    random_str = random_string()

    form = {
        'adid': adid,
        'email': email,
        'password': password,
        'format': 'json',
        'device_id': device_id,
        'cpl': 'true',
        'family_device_id': device_id,
        'locale': 'en_US',
        'client_country_code': 'US',
        'credentials_type': 'device_based_login_password',
        'generate_session_cookies': '1',
        'generate_analytics_claim': '1',
        'generate_machine_id': '1',
        'source': 'login',
        'machine_id': random_str,
        'api_key': '882a8490361da98702bf97a021ddc14d',
        'access_token': '350685531728%7C62f8ce9f74b12f84c123cc23437a4a32',
    }

    form['sig'] = encode_sig(form)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }

    url = 'https://b-graph.facebook.com/auth/login'

    try:
        response = requests.post(url, data=form, headers=headers)
        data = response.json()

        if response.status_code == 200 and 'access_token' in data:
            full_token = data['access_token']
            printf(Panel(f'[green]Generated Token: {full_token}[/green]', width=60, border_style="green"))
            return full_token
        else:
            error_message = data.get("error", {}).get("message", "Unknown error")
            printf(Panel(f'[red]Failed to generate token: {error_message}[/red]', width=60, border_style="red"))
            return None
    except requests.exceptions.RequestException as e:
        printf(Panel(f'[red]Network Error: {str(e)}[/red]', width=60, border_style="red"))
        return None

def post_comment(message, access_token, post_id, comment_limit):
    """Post comments on a Facebook post with rate limiting."""
    comment_url = f'https://graph.facebook.com/{post_id}/comments'
    
    printf("\n[bold yellow]Processing...[/bold yellow]\n")

    for i in range(comment_limit):
        data = {'message': message, 'access_token': access_token}
        response = requests.post(comment_url, data=data)

        if response.status_code == 200:
            printf(Panel(f'[green]Comment {i+1} posted successfully.[/green]', width=60, border_style="green"))
        else:
            error_info = response.json().get("error", {}).get("message", "Unknown error")
            printf(Panel(f'[red]Error posting comment {i+1}: {error_info}[/red]', width=60, border_style="red"))
        
        time.sleep(random.uniform(2, 5))  # Random delay to prevent spam detection

def main_menu():
    """Main menu for the user."""
    while True:
        console.print("\n[1] Generate Token")
        console.print("[2] Auto Comment on Post")
        console.print("[3] Exit")
        choice = input("\nSelect an option: ")

        if choice == "1":
            email = input("Enter your email: ").strip()
            password = getpass.getpass("Enter your password (hidden): ").strip()
            token = generate_token(email, password)

            if token:
                input("\nPress Enter to continue...")

        elif choice == "2":
            access_token = input("\nEnter your access token: ").strip()
            post_id = input("Enter your post ID: ").strip()
            comment_message = input("Enter comment message: ").strip()

            try:
                comment_limit = int(input("Enter comment limit: "))
                if comment_limit < 1:
                    raise ValueError
            except ValueError:
                printf("[red]Invalid number. Enter a positive integer.[/red]")
                continue

            post_comment(comment_message, access_token, post_id, comment_limit)
            input("\nPress Enter to continue...")

        elif choice == "3":
            console.print("[bold red]Exiting... Goodbye![/bold red]")
            time.sleep(1)
            break
        else:
            console.print("[red]Invalid choice! Try again.[/red]")
            time.sleep(1)

if __name__ == '__main__':
    main_menu()
