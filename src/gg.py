import json
import random
import requests
import urllib.parse # Potentially useful for more robust URL parsing, but simple split might suffice here.

def fetch_ips():
    """
    Fetches a list of IPv4 addresses from a GitHub repository.
    Returns a dictionary with an 'ipv4' key containing the list of IPs,
    or a fallback list if fetching fails.
    """
    try:
        response = requests.get('https://raw.githubusercontent.com/1384amir/ipscan/refs/heads/main/ip.json')
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        # Ensure data has the expected structure
        if not isinstance(data, dict) or 'ipv4' not in data or not isinstance(data['ipv4'], list):
             print("هشدار: ساختار داده دریافتی از منبع IP غیرمنتظره است.")
             return {"ipv4": ["162.159.254.110", "104.22.34.132"]} # Fallback
        return data
    except requests.exceptions.RequestException as e:
        print(f"خطا در واکشی IP ها: {e}. استفاده از IP های جایگزین.")
        return {"ipv4": ["162.159.254.110", "104.22.34.132"]} # Fallback IPs
    except json.JSONDecodeError:
         print("خطا در خواندن JSON از منبع IP. استفاده از IP های جایگزین.")
         return {"ipv4": ["162.159.254.110", "104.22.34.132"]} # Fallback IPs
    except Exception as e:
        print(f"خطای ناشناخته در واکشی IP ها: {e}. استفاده از IP های جایگزین.")
        return {"ipv4": ["162.159.254.110", "104.22.34.132"]} # Fallback IPs


def update_endpoints(config_file, use_random_ip=False, fixed_ip="162.159.192.23"):
    """
    Reads a JSON file containing a list of warp:// URLs, updates the IP
    address in each URL, and writes the modified list back to the file.

    Args:
        config_file (str): The path to the JSON file.
        use_random_ip (bool): If True, fetches a random IP from fetch_ips.
                               If False, uses the provided fixed_ip.
        fixed_ip (str): The fixed IP address to use when use_random_ip is False.
                        (Note: The port from this string is IGNORED; the original
                         port from each URL is preserved).
    """
    try:
        # Read the JSON file
        with open(config_file, 'r', encoding='utf-8') as file: # Specify encoding
            data = json.load(file)

        # Ensure the data is a list
        if not isinstance(data, list):
            print(f"خطا: فایل '{config_file}' حاوی لیست JSON معتبر نیست.")
            return

        # Determine the target IP address
        target_ip = ""
        if use_random_ip:
            ips_data = fetch_ips()
            ipv4_list = ips_data.get('ipv4', [])

            # Use fallback IP if no random IPs are available
            if not ipv4_list:
                print("هیچ IP معتبری برای استفاده یافت نشد. استفاده از IP ثابت جایگزین.")
                target_ip = fixed_ip
            else:
                # Filter for 162 IPs if desired (based on original code comment, though not implemented there)
                # filtered_ips = [ip for ip in ipv4_list if ip.startswith("162.")]
                # if filtered_ips:
                #     target_ip = random.choice(filtered_ips)
                # else:
                #     print("هشدار: هیچ IP با شروع 162 یافت نشد. استفاده از هر IP موجود یا ثابت جایگزین.")
                #     target_ip = random.choice(ipv4_list) if ipv4_list else fixed_ip
                target_ip = random.choice(ipv4_list) # Use any random IP if available

        else:
            target_ip = fixed_ip

        print(f"IP هدف برای به‌روزرسانی: {target_ip}")

        # List to hold the updated URLs
        updated_urls = []
        modified_count = 0

        # Iterate through the list of URLs
        for url_string in data:
            # Ensure the item is a string before processing
            if not isinstance(url_string, str):
                updated_urls.append(url_string) # Keep non-string items as they are
                continue

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

                    host_port_part = parts_after_warp[:end_of_host_port_index]
                    rest_of_url = parts_after_warp[end_of_host_port_index:]

                    # Split the host:port part to get the original port
                    ip_port_split = host_port_part.split(':')

                    if len(ip_port_split) == 2:
                        original_port = ip_port_split[1]
                        # Construct the new URL with the target IP and original port
                        new_url = f"warp://{target_ip}:{original_port}{rest_of_url}"
                        updated_urls.append(new_url)
                        modified_count += 1
                    else:
                        # Handle cases where the format is unexpected (e.g., no port)
                        print(f"هشدار: فرمت 'IP:PORT' در بخش '{host_port_part}' یافت نشد. URL اصلی حفظ می‌شود: {url_string}")
                        updated_urls.append(url_string)

                except Exception as e:
                    print(f"خطا در پردازش URL '{url_string}': {e}. URL اصلی حفظ می‌شود.")
                    updated_urls.append(url_string)
            else:
                # If it's not a warp:// URL, keep it as is
                updated_urls.append(url_string)

        # Write the modified list back to the file
        with open(config_file, 'w', encoding='utf-8') as file: # Specify encoding
            # use ensure_ascii=False to correctly write non-ASCII characters (like emojis)
            json.dump(updated_urls, file, indent=2, ensure_ascii=False)

        print(f"فایل '{config_file}' با موفقیت به‌روزرسانی شد. تعداد {modified_count} URL به استفاده از IP: {target_ip} تغییر یافت.")

    except FileNotFoundError:
        print(f"خطا: فایل پیکربندی '{config_file}' یافت نشد.")
    except json.JSONDecodeError:
        print(f"خطا: فایل '{config_file}' حاوی JSON معتبر نیست. اطمینان حاصل کنید که فرمت یک لیست از رشته‌ها است.")
    except Exception as e:
        print(f"خطا رخ داد: {str(e)}")

if __name__ == "__main__":
    # Define the path to your JSON configuration file
    config_file = 'frag.json'

    # --- Choose your update mode ---

    # Option 1: Use a random IP fetched from the online source
    # The script will fetch IPs and pick one randomly.
    # If fetching fails, it will use the 'fixed_ip' provided in the function definition as a fallback.
    update_endpoints(config_file, use_random_ip=True)

    # Option 2: Use a specific fixed IP address
    # Uncomment the line below and comment the line above to use a fixed IP.
    # The IP '196.198.101.0' is used as the target IP. The port in the original URLs will be preserved.
    # update_endpoints(config_file, use_random_ip=False, fixed_ip="196.198.101.0")

    # Note: The 'fixed_ip' parameter only provides the IP address to use when use_random_ip is False
    # or as a fallback. The original port from each URL is always kept.
