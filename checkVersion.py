#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup
import re

# URL of the older versions page
older_versions_url = "https://owncloud.com/older-versions/"

# Dictionary containing versions and their corresponding dates
versions_dict = {
    "10.13.4": "20231213",
    "10.13.3": "20231121",
    "10.13": "20231121",
    "10.13.3-rc.2": "20231117",
    "10.13.2": "20231009",
    "10.13.2-rc.1": "20231005",
    "10.13.2-beta.1": "20231004",
    "10.13.1": "20230906",
    "10.13": "20230822",    
    "10.13.0": "20230822",
    "10.12.2": "20230606",
    "10.12": "20230606",
    "10.12.1": "20230415",
    "10.12.0": "20230313",
    "10.11.0": "20220919",
    "10.11": "20220919",
    "10.10.0": "20220518",
    "10.10": "20220518",
    "10.9.1": "20220112",
    "10.9": "20220112",
    "10.9.0": "20211220",
    "10.8.0": "20210721",
    "10.8": "20210721",
    "10.7.0": "20210326",
    "10.7": "20210326",
    "10.6.0": "20201216",
    "10.6": "20201216",
    "10.5.0": "20200731",
    "10.5": "20200731"
}

def get_mobile_app_versions(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error fetching mobile app page. URL: {url}, Status code: {response.status_code}")
            return None, None

        soup = BeautifulSoup(response.content, 'html.parser')

        # Function to extract version number
        def extract_version(text):
            match = re.search(r"Version: (\d+\.\d+)", text)
            return match.group(1) if match else None

        # Extracting iOS version
        ios_version = None
        ios_version_div = soup.find('div', id="MobileApps Apple")
        if ios_version_div:
            ios_version_text = ios_version_div.find_previous('p').text
            ios_version = extract_version(ios_version_text)

        # Extracting Android version
        android_version = None
        android_version_div = soup.find('div', id="MobileApps GooglePlay")
        if android_version_div:
            android_version_text = android_version_div.find_previous('p').text
            android_version = extract_version(android_version_text)

        return ios_version, android_version
    except Exception as e:
        print(f"Exception occurred while fetching mobile app page: {str(e)}")
        return None, None

# Example usage
ios_version, android_version = get_mobile_app_versions("https://owncloud.com/mobile-apps/")


def get_desktop_versions(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error fetching desktop app page. URL: {url}, Status code: {response.status_code}")
            return None, None, None

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extracting Mac OS version
        mac_version_link = soup.find('a', href=lambda href: "mac" in href and "ownCloud-" in href)
        mac_version = mac_version_link['href'].split('/')[-1].split('-')[1].split('.')[0:3] if mac_version_link else "Not found"
        mac_version = '.'.join(mac_version) if mac_version != "Not found" else mac_version

        # Extracting Windows version
        windows_version_link = soup.find('a', href=lambda href: "win" in href and "ownCloud-" in href)
        windows_version = windows_version_link['href'].split('/')[-1].split('-')[1].split('.')[0:3] if windows_version_link else "Not found"
        windows_version = '.'.join(windows_version) if windows_version != "Not found" else windows_version

        # Extracting Linux version from the specific div tag
        linux_version_elements = soup.find_all('div', class_='et_pb_text_inner')
        linux_version = None
        for element in linux_version_elements:
            version_text = element.text.strip()
            # Looking for version number in the format x.x.x
            version_parts = version_text.split('.')
            if len(version_parts) == 3 and all(part.isdigit() for part in version_parts):
                linux_version = version_text
                break
        linux_version = linux_version if linux_version else "Not found"

        return mac_version, windows_version, linux_version
    except Exception as e:
        print(f"Exception occurred while fetching desktop app page: {str(e)}")
        return None, None, None

def get_version_from_download_page(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error fetching download page. URL: {url}, Status code: {response.status_code}")
            return None, None

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extracting Infinite Scale version
        infinite_scale_element = soup.find('a', href=lambda href: href and "download.owncloud.com/ocis/ocis/stable" in href)
        infinite_scale_version = None
        if infinite_scale_element:
            infinite_scale_version = infinite_scale_element.text.strip().split()[-1]

        # Extracting OwnCloud Server version
        owncloud_server_elements = soup.find_all('div', class_="et_pb_text_inner")
        owncloud_server_version = None
        for element in owncloud_server_elements:
            text = element.text.strip()
            if text.count('.') == 2 and all(part.isdigit() for part in text.split('.')):  # Improved check for 'x.x.x' format
                owncloud_server_version = text
                break

        return infinite_scale_version, owncloud_server_version
    except Exception as e:
        print(f"Exception occurred while fetching download page: {str(e)}")
        return None, None


def get_latest_version_from_changelog(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error fetching changelog page. URL: {url}, Status code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        if "ios-app" in url:
            # Specific logic for the iOS app changelog page
            links = soup.find_all('a', href=lambda href: href and "changelog-for-owncloud-ios-client" in href)
            for link in links:
                version_candidate = link.text.strip().split()[-1]  # Get the last word, which should be the version
                if is_valid_version_format(version_candidate):
                    return version_candidate
        else:
            # General logic for other changelog pages
            links = soup.find_all('a')
            for link in links:
                version_candidate = link.text.strip()
                if is_valid_version_format(version_candidate) and all(x not in version_candidate for x in ['alpha', 'beta', 'rc']):
                    if check_link(link['href']):
                        return version_candidate
        return None
    except Exception as e:
        print(f"Exception occurred while fetching changelog: {str(e)}")
        return None

# Function to check if the link is valid
def check_link(url):
    try:
        response = requests.head(url, allow_redirects=True)
        if response.status_code != 200:
            return False
        return True
    except Exception:
        return False

# Function to extract version from URL or dictionary
def extract_version(url, versions_dict):
    # First, use dictionary to match dates
    for version, date in versions_dict.items():
        if date in url:
            return version

    # Then, extract version from the URL for server and desktop links
    url_parts = url.split('/')
    for part in url_parts:
        # Handle Server Package version format: "owncloud-x.x.x"
        if '/server/' in url and 'owncloud-' in part:
            version_parts = part.split('owncloud-')[1].split('.')[0:3]
            return '.'.join(version_parts)
        
        # Handle Desktop Client version formats
        if '/desktop/' in url:
            # Format: "ownCloud-x.x.x"
            if 'ownCloud-' in part:
                version_parts = part.split('ownCloud-')[1].split('.')[0:3]
                return '.'.join(version_parts)
            # Formats: "/stable/x.x.x" and "/stable//x.x.x"
            elif '/stable/' in part:
                version_candidate = part.replace('//', '/').split('/')[-1]
                if version_candidate.count('.') == 2:
                    return version_candidate

    return "Unknown"

# Function to check if a version string is in the "x.x.x" format
def is_valid_version_format(version_str):
    parts = version_str.split('.')
    return len(parts) == 3 and all(part.isdigit() for part in parts)

# Main script
def main():
    print("checking 'https://owncloud.com/older-versions':\n")

    try:
        page_response = requests.get(older_versions_url)
        if page_response.status_code != 200:
            print(f"Error fetching the older versions page. Status code: {page_response.status_code}")
            return

        soup = BeautifulSoup(page_response.content, 'html.parser')

        server_versions = set()
        desktop_versions = set()
        server_links = 0
        desktop_links = 0

        # Process each download link
        download_links = soup.find_all('a', href=lambda href: "https://download." in href)
        for link in download_links:
            url = link['href']
            version = extract_version(url, versions_dict)
            if version == "Unknown":
                version = url.split('/')[-1].split('.')[0]

            if "/desktop/" in url and not is_valid_version_format(version):
                continue

            if "/server/" in url:
                server_versions.add(version)
                server_links += 1
                if not check_link(url):
                    print(f"Non-working Server Package URL: {url}, Version: {version}\n")

            elif "/desktop/" in url:
                desktop_versions.add(version)
                desktop_links += 1
                if not check_link(url):
                    print(f"Non-working Desktop Client URL: {url}, Version: {version}\n")

        print(f"\nTotal Server Package versions: {len(server_versions)}, Total links: {server_links}")
        print(f"Total Desktop Client versions: {len(desktop_versions)}, Total links: {desktop_links}\n")

        # Titles for the changelog sections
        print("Latest versions from changelog:\n")

        # URLs of the changelog pages and their corresponding titles
        changelog_urls = {
            "https://owncloud.com/changelog/infinite-scale/": "Infinite-scale",
            "https://owncloud.com/changelog/server": "ownCloud Server",
            "https://owncloud.com/changelog/desktop": "Desktop Client",
            "https://owncloud.com/changelog/ios-app": "iOS App",
            "https://owncloud.com/changelog/android-app": "Android App"
        }

        # Fetch and print the latest version for each changelog
        changelog_versions = {}
        for url, title in changelog_urls.items():
            latest_version = get_latest_version_from_changelog(url)
            if latest_version:
                print(f"{title}: {latest_version}")
                changelog_versions[title] = latest_version
            else:
                print(f"{title}: No valid latest version found")
        
        # Fetch mobile app versions
        mobile_app_url = "https://owncloud.com/mobile-apps/"
        ios_app_version, android_app_version = get_mobile_app_versions(mobile_app_url)

        # Fetch changelog versions
        ios_changelog_version = changelog_versions.get("iOS App", "Not found in changelog")
        android_changelog_version = changelog_versions.get("Android App", "Not found in changelog")
        
        # Fetching versions from the download page
        download_page_url = "https://owncloud.com/download-server/"
        infinite_scale_download_version, owncloud_server_download_version =     get_version_from_download_page(download_page_url)
        desktop_app_url = "https://owncloud.com/desktop-app/"
        mac_version, windows_version, linux_version = get_desktop_versions(desktop_app_url)

        changelog_desktop_version = changelog_versions.get("Desktop Client", "Not found in changelog")

        # Comparing download page with changelog
        print("\nComparing download page with changelog:\n")
        print("\nDesktop app versions from 'https://owncloud.com/desktop-app/':")
        print(f"Mac OS Version: {mac_version}, from changelog: {changelog_desktop_version} ({'They are Same' if mac_version == changelog_desktop_version else 'They are Different'})")
        print(f"Windows Version: {windows_version}, from changelog: {changelog_desktop_version} ({'They are Same' if windows_version == changelog_desktop_version else 'They are Different'})")
        print(f"Linux Version: {linux_version}, from changelog: {changelog_desktop_version} ({'They are Same' if linux_version == changelog_desktop_version else 'They are Different'})\n")
        # Comparing mobile app versions with changelog
        print("\nMobile app versions from 'https://owncloud.com/mobile-apps/':")
        print(f"iOS Version: {ios_app_version}, from changelog: {ios_changelog_version} ({'They are Same' if ios_app_version == ios_changelog_version else 'They are Different'})")
        print(f"Android Version: {android_app_version}, from changelog: {android_changelog_version} ({'They are Same' if android_app_version == android_changelog_version else 'They are Different'})\n")
        if infinite_scale_download_version:
            changelog_version = changelog_versions.get("Infinite-scale", "Not found in changelog")
            print(f"Infinite-scale version from '{download_page_url}': {infinite_scale_download_version}, from changelog; {changelog_version} ({'They are Same' if infinite_scale_download_version == changelog_version else 'They are Different'})")

        if owncloud_server_download_version:
            changelog_version = changelog_versions.get("ownCloud Server", "Not found in changelog")
            print(f"ownCloud Server version from '{download_page_url}': {owncloud_server_download_version}, from changelog; {changelog_version} ({'They are Same' if owncloud_server_download_version == changelog_version else 'They are Different'})")

    except Exception as e:
        print(f"Exception occurred: {str(e)}")

# Run the script
main()
