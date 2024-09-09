import json
import os
import pathlib
import time
from collections import defaultdict
from datetime import datetime, timedelta
from urllib.parse import parse_qs, unquote, urlparse

import click
import pyotp
import requests

DB_FILE = pathlib.Path.home() / ".local/share/ente-totp/db.json"
ICONS_FOLDER = pathlib.Path.home() / ".local/share/ente-totp/icons"
LOGO_DEV_API_URL = "https://img.logo.dev/{domain}?token={api_key}"

# Get the API key from environment variable
LOGO_DEV_API_KEY = "pk_T0ZUG4poQGqfGcFoeCpRww"


@click.group()
def cli():
    pass


@cli.command("import")
@click.argument("file", type=click.Path(exists=True))
def import_file(file):
    secret_dict = defaultdict(list)
    for service_name, username, secret in parse_secrets(file):
        secret_dict[service_name].append((username, secret))
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DB_FILE.open("w") as json_file:
        json.dump(secret_dict, json_file, indent=2)
    print("Database created.")


def parse_secrets(file_path="secrets.txt"):
    secrets_list = []

    with open(file_path, "r") as secrets_file:
        for line in secrets_file:
            line = line.strip()
            if line:
                parsed_url = urlparse(line)
                if parsed_url.scheme == "otpauth":
                    path_items = unquote(parsed_url.path).strip("/").split(":", 1)
                    if len(path_items) == 2:
                        service_name, username = path_items[0], path_items[1]
                    else:
                        service_name, username = path_items[0].strip(":"), ""
                    query_params = parse_qs(parsed_url.query)
                    secret = query_params.get("secret", [None])[0]
                    if secret:
                        secrets_list.append((service_name, username, secret))

    return secrets_list


def format_data(
    service_name, username, current_totp, next_totp, time_remaining, output_type
):
    """Format the data based on the output type."""
    time_unit = "second" if time_remaining == 1 else "seconds"
    subset = f"Current TOTP: {current_totp} | Next TOTP: {next_totp}, {time_remaining} {time_unit} left"

    icon_path = get_icon_path(service_name)

    if output_type == "alfred":
        title = f"{service_name} - {username}" if username else service_name
        return {
            "title": title,
            "subtitle": subset,
            "arg": current_totp + "," + next_totp,
            "icon": {"path": str(icon_path)},
        }

    elif output_type == "json":
        return {
            "service_name": service_name,
            "username": username,
            "current_totp": current_totp,
            "next_totp": next_totp,
            "time_remaining": time_remaining,
            "service_data": subset,
            "icon_path": str(icon_path),
        }

    return None


def download_icon(service_name):
    """Download icon for a given service using Logo.dev API."""
    if not LOGO_DEV_API_KEY:
        print("LOGO_DEV_API_KEY is not set. Skipping icon download.")
        return

    # Remove spaces from service_name and convert to lowercase
    sanitized_service_name = service_name.replace(" ", "").lower()

    # Assume the domain is sanitized_service_name.com
    domain = f"{sanitized_service_name}.com"
    icon_url = LOGO_DEV_API_URL.format(domain=domain, api_key=LOGO_DEV_API_KEY)
    icon_path = ICONS_FOLDER / f"{sanitized_service_name}.png"

    if not icon_path.exists():
        response = requests.get(icon_url, timeout=5)
        if response.status_code == 200:
            with open(icon_path, "wb") as icon_file:
                icon_file.write(response.content)


def download_icons(services):
    """Download icons for all services."""
    ICONS_FOLDER.mkdir(parents=True, exist_ok=True)

    for service in services:
        download_icon(service)


def get_icon_path(service_name):
    sanitized_service_name = service_name.replace(" ", "").lower()
    icon_path = ICONS_FOLDER / f"{sanitized_service_name}.png"

    if icon_path.exists():
        return icon_path
    return "icon.png"


@cli.command("get")
@click.argument("secret_id")
@click.option(
    "-o",
    "output_format",
    type=click.Choice(["json", "alfred"]),
    default="json",
    help="Data output format",
)
def generate_totp(secret_id, output_format):
    try:
        with open(DB_FILE, "r") as file:
            data = json.load(file)
        items = []  # Collect all items in this list
        services_to_download = set()  # Collect services that need icon download

        for service_name, service_data in data.items():
            if secret_id.lower() in service_name.lower():
                for username, secret in service_data:
                    totp = pyotp.TOTP(secret)
                    current_time = datetime.now()
                    current_totp = totp.now()
                    next_time = current_time + timedelta(seconds=30)
                    next_totp = totp.at(next_time)

                    # Calculate time remaining
                    time_step = 30  # TOTP default time step
                    time_remaining = time_step - (current_time.timestamp() % time_step)
                    time_remaining = int(time_remaining)  # Convert to integer

                    formatted_data = format_data(
                        service_name,
                        username,
                        current_totp,
                        next_totp,
                        time_remaining,
                        output_format,
                    )
                    if formatted_data:
                        items.append(formatted_data)
                        services_to_download.add(service_name)

        # Download icons after search is complete
        download_icons(services_to_download)

        print(json.dumps({"items": items}, indent=4))

    except Exception as e:
        print(json.dumps({"items": [], "error": str(e)}, indent=4))


if __name__ == "__main__":
    cli()
