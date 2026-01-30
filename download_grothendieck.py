import requests
import os
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed

# Disable SSL warnings (server has expired certificate)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://grothendieck.umontpellier.fr/"
OUTPUT_DIR = "grothendieck_archives"

PDF_FILES = [
    "1.pdf", "2.pdf", "4.pdf", "5.pdf", "6.pdf", "7.pdf", "8.pdf", "9.pdf",
    "10.pdf", "11.pdf", "12.pdf", "13.pdf", "14.pdf", "15.pdf", "16.pdf",
    "18.pdf", "19.pdf", "21.pdf", "22.pdf", "23.pdf", "24.pdf", "25.pdf",
    "26.pdf", "27.pdf", "28.pdf", "29.pdf", "31.pdf", "32.pdf", "33.pdf",
    "34.pdf", "35.pdf", "36.pdf", "37.pdf", "39.pdf", "40.pdf", "41.pdf",
    "42.pdf", "43.pdf", "44.pdf", "45.pdf", "46.pdf", "47.pdf", "48.pdf",
    "49.pdf", "50.pdf", "51.pdf", "52.pdf", "53.pdf", "54.pdf", "55.pdf",
    "56.pdf", "57.pdf", "58.pdf", "59.pdf", "60.pdf", "62.pdf", "63.pdf",
    "64.pdf", "66.pdf", "67.pdf", "68.pdf", "69.pdf", "70.pdf", "71.pdf",
    "72.pdf", "73.pdf", "74.pdf", "75.pdf", "76.pdf", "77.pdf", "78.pdf",
    "79.pdf", "80.pdf", "81.pdf", "82.pdf", "83.pdf", "84.pdf", "85.pdf",
    "86.pdf", "87.pdf", "88.pdf", "89.pdf", "90.pdf", "91.pdf", "92.pdf",
    "93.pdf", "94.pdf", "95.pdf", "96.pdf", "97.pdf", "98.pdf", "99.pdf",
    "100.pdf", "101.pdf", "102.pdf", "103.pdf", "104.pdf", "105.pdf", "106.pdf",
    "107.pdf", "108.pdf", "109.pdf", "110.pdf", "111.pdf", "112.pdf", "113.pdf",
    "114.pdf", "115.pdf", "116.pdf", "117.pdf", "118.pdf", "119.pdf", "120.pdf",
    "121.pdf", "122.pdf", "123.pdf", "124.pdf", "125.pdf", "126.pdf", "127.pdf",
    "128.pdf", "129.pdf", "130.pdf", "131.pdf", "132.pdf", "133.pdf", "134.pdf",
    "135.pdf", "136.pdf", "137.pdf", "138.pdf", "139.pdf", "140.pdf", "141.pdf",
    "142.pdf", "143.pdf", "144.pdf", "145.pdf", "146.pdf", "147.pdf", "148.pdf",
    "149.pdf", "150.pdf", "151.pdf", "152.pdf", "153.pdf", "154.pdf", "155.pdf",
    "156.pdf", "157.pdf", "158.pdf", "159.pdf", "160.pdf",
    "162-1.pdf", "162-2.pdf", "162-3.pdf", "162-4.pdf", "162-5.pdf", "162-6.pdf"
]

def download_pdf(filename):
    url = BASE_URL + filename
    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        response = requests.get(url, timeout=60, verify=False)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return (filename, True, len(response.content))
        return (filename, False, response.status_code)
    except Exception as e:
        return (filename, False, str(e))

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Downloading {len(PDF_FILES)} PDFs to '{OUTPUT_DIR}/'...")
    
    success, failed = 0, 0
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(download_pdf, f): f for f in PDF_FILES}
        for future in as_completed(futures):
            filename, ok, info = future.result()
            if ok:
                success += 1
                print(f"[OK] {filename} ({info:,} bytes)")
            else:
                failed += 1
                print(f"[FAIL] {filename} - Error: {info}")
    
    print(f"\nComplete: {success} downloaded, {failed} failed")

if __name__ == "__main__":
    main()
