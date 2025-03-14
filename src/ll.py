import json
import random
import requests

def fetch_ips():
    try:
        response = requests.get('https://raw.githubusercontent.com/ircfspace/endpoint/refs/heads/main/ip.json')
        data = response.json()
        return data
    except Exception as e:
        return {
            "ipv4": ["162.159.192.23:859", "162.159.192.178:4500"]
        }

def update_endpoints(config_file, use_random_ip=False, fixed_ip="162.159.192.23:859"):
    try:
        # Read the JSON file
        with open(config_file, 'r') as file:
            data = json.load(file)
        
        # Determine new endpoint value
        if use_random_ip:
            ips = fetch_ips()
            ipv4_list = [ip for ip in ips['ipv4'] if ip.startswith("162.")]
            
            if not ipv4_list:
                print("هیچ IP با شروع 162 پیدا نشد.")
                return
                
            new_endpoint = random.choice(ipv4_list)
        else:
            new_endpoint = fixed_ip
        
        # Function to recursively update 'endpoint' values
        def update_endpoint_recursive(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key.lower() == 'endpoint':
                        obj[key] = new_endpoint
                    else:
                        update_endpoint_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    update_endpoint_recursive(item)
        
        # Update all 'endpoint' values
        update_endpoint_recursive(data)
        
        # Write the modified JSON back to file
        with open(config_file, 'w') as file:
            json.dump(data, file, indent=2)
            print(f"Endpoint به {new_endpoint} تغییر یافت.")
            
    except FileNotFoundError:
        print(f"خطا: فایل '{config_file}' یافت نشد.")
    except json.JSONDecodeError:
        print("خطا: فایل JSON معتبر نیست.")
    except Exception as e:
        print(f"خطا رخ داد: {str(e)}")

if __name__ == "__main__":
    config_file = 'oop.json'  # Replace with your JSON file path
    
    # Use fixed IP (196.198.101.0)
    update_endpoints(config_file, use_random_ip=True)
    
    # Uncomment the line below and comment the above line if you want random IP instead
    # update_endpoints(config_file, use_random_ip=True)
