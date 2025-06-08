#!/usr/bin/env python3
# Script de détection Evil Twin v1.2 - À exécuter sur machine Linux
import subprocess
import re
import time

print("[+] Démarrage du scan de sécurité Wi-Fi...\n")

def scan_wifi():
    """Capture les réseaux Wi-Fi environnants avec leurs signatures techniques"""
    try:
        result = subprocess.check_output(["iwlist", "scan"], text=True, stderr=subprocess.STDOUT)
        return result
    except subprocess.CalledProcessError:
        print("⚠️  Activez le mode moniteur Wi-Fi d'abord :")
        print("sudo airmon-ng start wlan0")
        exit(1)

def detect_evil_twin(scan_data):
    """Analyse les empreintes réseaux pour repérer les doublons suspects"""
    networks = {}
    current_ssid = None
    
    for line in scan_data.split('\n'):
        # Détection SSID (nom réseau)
        ssid_match = re.search(r'ESSID:"(.*?)"', line)
        if ssid_match:
            current_ssid = ssid_match.group(1)
            if current_ssid not in networks:
                networks[current_ssid] = []
        
        # Détection BSSID (adresse physique routeur)
        mac_match = re.search(r'Address: (([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})', line)
        if mac_match and current_ssid:
            bssid = mac_match.group(0).split(' ')[1]
            networks[current_ssid].append(bssid)
    
    # Analyse des doublons
    red_flags = []
    for ssid, bssids in networks.items():
        if len(bssids) > 1:
            red_flags.append(f"ALERTE : '{ssid}' a {len(bssids)} routeurs différents (BSSID : {', '.join(bssids)})")
    
    return red_flags

if __name__ == "__main__":
    # Double scan pour éviter les faux positifs
    first_scan = detect_evil_twin(scan_wifi())
    time.sleep(10)
    second_scan = detect_evil_twin(scan_wifi())
    
    # Comparaison des résultats
    alerts = set(first_scan) & set(second_scan)
    
    if alerts:
        print("\033[91m" + "🚨 ATTENTION : Evil Twin détecté !" + "\033[0m")
        for alert in alerts:
            print(f"- {alert}")
        print("\n🔍 Conseil : Déconnectez-vous immédiatement et signalez à votre service IT.")
    else:
        print("\033[92m" + "✅ Aucun Evil Twin détecté" + "\033[0m")
    
    print("\nℹ️ Explication technique :")
    print("Un attaquant clone votre réseau légitime (même nom Wi-Fi) mais avec une adresse physique différente (BSSID).")