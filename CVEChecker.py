import json
import os
import time
import requests

print('hello')
# Load package data from same directory
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, "package_data.json")

with open(json_path, "r") as file:
    data = json.load(file)


# Utility: version comparison
def compare_versions(v1, v2):
    def normalize(v):
        v = v.split('-')[0]
        parts = v.split('.')
        normalized = []
        for part in parts:
            num = ''.join(filter(str.isdigit, part))
            suffix = ''.join(filter(str.isalpha, part))
            normalized.append((int(num) if num else 0, suffix))
        return normalized

    parts1 = normalize(v1)
    parts2 = normalize(v2)

    # Pad shorter version with (0, '') to equalize length
    length = max(len(parts1), len(parts2))
    parts1 += [(0, '')] * (length - len(parts1))
    parts2 += [(0, '')] * (length - len(parts2))

    for p1, p2 in zip(parts1, parts2):
        if p1[0] != p2[0]:
            return -1 if p1[0] < p2[0] else 1
        if p1[1] != p2[1]:
            return -1 if p1[1] < p2[1] else 1

    return 0

# Fetch CVE data
def fetch_cve_data(cve_id):
    url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve_id}"
    try:
        response = requests.get(url, headers = '')
        if response.status_code == 429:
            print(f"Rate limited on {cve_id}, sleeping for 10s...")
            time.sleep(10)
            return fetch_cve_data(cve_id)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching {cve_id}: {e}")
        return None

# Main loop
for key, pkg in data.items():
    pkg_name = pkg["package_name"]
    pkg_version = pkg["package_version"]
    cves = pkg.get("cves", [])

    matching = []
    non_matching = []

    for cve_id in cves:
        cve_data = fetch_cve_data(cve_id)
        time.sleep(2)  # Avoid rate limits

        if not cve_data:
            non_matching.append(cve_id)
            continue

        match_found = False
        for vuln in cve_data.get("vulnerabilities", []):
            for config in vuln.get("cve", {}).get("configurations", []):
                for node in config.get("nodes", []):
                    for cpe in node.get("cpeMatch", []):
                        criteria = cpe.get("criteria", "")
                        def cpe_matches(criteria, cpe_name):
                            parts1 = criteria.split(':')
                            parts2 = cpe_name.split(':')
                            if len(parts1) != len(parts2):
                                return False
                            for a, b in zip(parts1, parts2):
                                if a != '*' and a != b:
                                    return False
                            return True

                        if not cpe_matches(criteria, pkg.get("cpe_name", "")):
                            continue
                        if not cpe.get("vulnerable", False):
                            continue

                        version_start_incl = cpe.get("versionStartIncluding")
                        version_start_excl = cpe.get("versionStartExcluding")
                        version_end_incl = cpe.get("versionEndIncluding")
                        version_end_excl = cpe.get("versionEndExcluding")

                        lower_ok = True
                        upper_ok = True

                        if version_start_incl:
                            lower_ok = compare_versions(pkg_version, version_start_incl) >= 0
                        elif version_start_excl:
                            lower_ok = compare_versions(pkg_version, version_start_excl) > 0

                        if version_end_incl:
                            upper_ok = compare_versions(pkg_version, version_end_incl) <= 0
                        elif version_end_excl:
                            upper_ok = compare_versions(pkg_version, version_end_excl) < 0

                        if lower_ok and upper_ok:
                            match_found = True
                            break
                    if match_found:
                        break
                if match_found:
                    break
            if match_found:
                break

        if match_found:
            matching.append(cve_id)
        else:
            non_matching.append(cve_id)

    pkg["matching_cves"] = matching
    pkg["non_matching_cves"] = non_matching
    pkg["matching_cve_count"] = len(matching)
    pkg["non_matching_cve_count"] = len(non_matching)

# Save updated output
output_path = os.path.join(script_dir, "updated_package_data.json")
final_json = []
for pkg in data.values():
    final_json.append({
        "package_name": pkg.get("package_name", ""),
        "package_version": pkg.get("package_version", ""),
        "cpe_name": pkg.get("cpe_name", ""),
        "cve_count": len(pkg.get("cves", [])),
        "matching_cve_count": pkg.get("matching_cve_count", 0),
        "non_matching_cve_count": pkg.get("non_matching_cve_count", 0),
        "matching_cves": pkg.get("matching_cves", []),
        "non_matching_cves": pkg.get("non_matching_cves", []),
    })

with open(output_path, "w") as f:
    json.dump(final_json, f, indent=2)

print("Results saved to updated_package_data.json")