import json # Still needed for fetch_ips, but not for reading/writing frog.txt
import random
import requests
import urllib.parse # Imported, but not strictly used in this version, kept for potential future use

def fetch_ips():
    """
    Fetches a list of IPv4 addresses (potentially with ports) from a GitHub repository.
    Returns a dictionary with an 'ipv4' key containing the list of IPs,
    or a fallback list if fetching fails.
    """
    try:
        # Using the new URL you provided
        response = requests.get('https://raw.githubusercontent.com/ircfspace/endpoint/refs/heads/main/ip.json')
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        # Ensure data has the expected structure
        if not isinstance(data, dict) or 'ipv4' not in data or not isinstance(data['ipv4'], list):
             print("هشدار: ساختار داده دریافتی از منبع IP غیرمنتظره است.")
             return {"ipv4": ["162.159.192.23:859", "162.159.192.178:4500"]} # Fallback
        return data
    except requests.exceptions.RequestException as e:
        print(f"خطا در واکشی IP ها: {e}. استفاده از IP های جایگزین.")
        return {"ipv4": ["162.159.192.23:859", "162.159.192.178:4500"]} # Fallback IPs
    except json.JSONDecodeError:
         print("خطا در خواندن JSON از منبع IP. استفاده از IP های جایگزین.")
         return {"ipv4": ["162.159.192.23:859", "162.159.192.178:4500"]} # Fallback IPs
    except Exception as e:
        print(f"خطای ناشناخته در واکشی IP ها: {e}. استفاده از IP های جایگزین.")
        return {"ipv4": ["162.159.192.23:859", "162.159.192.178:4500"]} # Fallback IPs


def update_urls_in_text_file(file_path, use_random_ip=False, fixed_ip="162.159.192.23:859"):
    """
    Reads a text file containing warp:// URLs (one per line), updates the IP and Port
    component in each URL, and writes the modified URLs back to the file.

    Args:
        file_path (str): The path to the text file.
        use_random_ip (bool): If True, fetches a random IP:PORT from fetch_ips.
                               If False, uses the provided fixed_ip (IP:PORT).
        fixed_ip (str): The fixed IP:PORT string to use when use_random_ip is False.
                        This entire string will be used for replacement.
    """
    try:
        # Read the URLs from the text file, one line per URL
        with open(file_path, 'r', encoding='utf-8') as file:
            # Read all lines, strip leading/trailing whitespace (including newlines)
            urls = [line.strip() for line in file if line.strip()] # Ignore empty lines

        if not urls:
            print(f"فایل '{file_path}' خالی است یا حاوی URL معتبری نیست.")
            return

        # Determine the target IP:PORT string (either random or fixed)
        target_ip_port = ""
        if use_random_ip:
            ips_data = fetch_ips()
            ipv4_list = ips_data.get('ipv4', [])

            # Filter for IPs starting with 162. (based on original code)
            # Note: This filter applies to the fetched IP:PORT strings
            filtered_ips = [ip for ip in ipv4_list if isinstance(ip, str) and ip.startswith("162.")]

            # Use fallback IP:PORT if no suitable random IPs are found after filtering
            if not filtered_ips:
                print("هیچ IP معتبری با شروع 162. برای استفاده یافت نشد. استفاده از IP ثابت جایگزین.")
                target_ip_port = fixed_ip
            else:
                target_ip_port = random.choice(filtered_ips)
        else:
            target_ip_port = fixed_ip

        if not target_ip_port:
             print("خطا: نتوانست IP:PORT هدف معتبری را استخراج کند. به‌روزرسانی انجام نشد.")
             return

        print(f"IP:PORT هدف برای جایگزینی: {target_ip_port}")

        # List to hold the updated URLs
        updated_urls = []
        modified_count = 0

        # Iterate through the list of URLs read from the file
        for url_string in urls:
            # Check if it's a warp:// URL
            if url_string.startswith("warp://"):
                try:
                    # Find the part after "warp://"
                    parts_after_warp = url_string.split("warp://", 1)[1]

                    # Find the end of the IP:PORT part (first occurrence of /, ?, or #)
                    end_of_host_port_index = len(parts_after_warp) # Default to end if no / ? #
                    for char in ['/', '?', '#']:
                         char_index = parts_after_warp.find(char)
                         if char_index != -1:
                             end_of_host_port_index = min(end_of_host_port_index, char_index)

                    # Extract the rest of the URL (path, query, fragment)
                    rest_of_url = parts_after_warp[end_of_host_port_index:]

                    # Construct the new URL with the target IP:PORT and the rest of the URL
                    new_url = f"warp://{target_ip_port}{rest_of_url}"
                    updated_urls.append(new_url)
                    modified_count += 1

                except Exception as e:
                    print(f"خطا در پردازش URL '{url_string}': {e}. URL اصلی حفظ می‌شود.")
                    updated_urls.append(url_string)
            else:
                # If it's not a warp:// URL, keep it as is
                updated_urls.append(url_string)

        # Write the modified list of URLs back to the text file, one per line
        with open(file_path, 'w', encoding='utf-8') as file:
            for url in updated_urls:
                file.write(url + '\n') # Write each URL followed by a newline

        print(f"فایل '{file_path}' با موفقیت به‌روزرسانی شد. تعداد {modified_count} URL به استفاده از IP:PORT: {target_ip_port} تغییر یافتند.")

    except FileNotFoundError:
        print(f"خطا: فایل '{file_path}' یافت نشد.")
    except Exception as e:
        print(f"خطا رخ داد: {str(e)}")

if __name__ == "__main__":
    # Define the path to your text file
    config_file = 'conf.txt' # Using 'frog.txt'

    # --- Choose your update mode ---

    # Option 1: Use a random IP:PORT fetched from the online source
    # The script will fetch IP:PORTs and pick one randomly that starts with "162.".
    # This entire chosen random IP:PORT will be used to update the IP:PORT part of URLs.
    # If fetching fails or no suitable IPs are found, it will use the 'fixed_ip'
    # provided below as a fallback.
    update_urls_in_text_file(config_file, use_random_ip=True)

    # Option 2: Use a specific fixed IP:PORT string
    # Uncomment the line below and comment the line above to use a fixed IP:PORT.
    # The entire string '196.198.101.0:1234' will be used to update the IP:PORT part of URLs.
    # update_urls_in_text_file(config_file, use_random_ip=False, fixed_ip="196.198.101.0:1234")

    # Note: The script now reads and writes a plain text file, treating each line as a URL.
    # It replaces the entire IP:PORT part of the warp:// URLs with the chosen target_ip_port string.
