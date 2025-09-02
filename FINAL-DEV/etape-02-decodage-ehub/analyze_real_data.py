"""
Analyse des messages eHuB réels de Unity
Pour comprendre le vrai format du protocole
"""

import struct

def analyze_real_message():
    """
    Analysons un message réel Unity capturé :
    b'eHuB\x02\x01\xaa\x06K\n\x1f\x8b\x08\x00...'
    """
    
    # Message réel capturé
    sample = b'eHuB\x02\x01\xaa\x06K\n\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\n'
    
    print("🔍 ANALYSE MESSAGE eHuB RÉEL")
    print("="*50)
    
    # Header bytes
    print(f"📋 Bytes 0-15: {sample[:16].hex(' ')}")
    print()
    
    # Signature
    signature = sample[0:4].decode('ascii')
    print(f"✅ Signature: '{signature}'")
    
    # Différentes interprétations du header
    print(f"📊 Byte 4 (type?): {sample[4]} = 0x{sample[4]:02X}")
    print(f"📊 Byte 5 (version?): {sample[5]} = 0x{sample[5]:02X}")
    print(f"📊 Bytes 6-7: {sample[6:8].hex(' ')}")
    print(f"📊 Bytes 8-11: {sample[8:12].hex(' ')}")
    print()
    
    # Tests différents formats
    print("🧪 TESTS FORMATS DIFFÉRENTS")
    print("-" * 30)
    
    # Format supposé actuel
    try:
        universe1 = struct.unpack('<H', sample[6:8])[0]
        length1 = struct.unpack('<I', sample[8:12])[0]
        print(f"🔹 Format actuel (little endian):")
        print(f"   Universe: {universe1}")
        print(f"   Length: {length1}")
    except:
        print("❌ Erreur format actuel")
    
    # Big endian
    try:
        universe2 = struct.unpack('>H', sample[6:8])[0]
        length2 = struct.unpack('>I', sample[8:12])[0]
        print(f"🔹 Format big endian:")
        print(f"   Universe: {universe2}")
        print(f"   Length: {length2}")
    except:
        print("❌ Erreur format big endian")
    
    # Format alternatif : length sur 2 bytes
    try:
        universe3 = struct.unpack('<H', sample[6:8])[0]
        length3 = struct.unpack('<H', sample[8:10])[0]
        print(f"🔹 Format length 2 bytes:")
        print(f"   Universe: {universe3}")
        print(f"   Length: {length3}")
        print(f"   Bytes 10-11: {sample[10:12].hex(' ')}")
    except:
        print("❌ Erreur format 2 bytes")
    
    print()
    print("🗜️  ANALYSE GZIP")
    print("-" * 20)
    
    # Chercher le début GZip dans les données
    for i in range(len(sample)-1):
        if sample[i:i+2] == b'\x1f\x8b':
            print(f"✅ Signature GZip trouvée à l'offset {i}")
            print(f"   Données GZip: {sample[i:i+10].hex(' ')}")
            break
    
    print()
    print("📏 LONGUEURS RÉELLES")
    print("-" * 20)
    print(f"🔹 Message total vu dans log: ~2643 bytes")
    print(f"🔹 Header supposé: 12 bytes")  
    print(f"🔹 Payload attendu: ~2631 bytes")
    print(f"🔹 Signature GZip à offset 10")
    print(f"🔹 => Header réel: 10 bytes seulement?")

if __name__ == "__main__":
    analyze_real_message()
