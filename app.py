import sys
sys.path.append("/")

from flask import Flask, jsonify, request
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import binascii
import os
import warnings
from urllib3.exceptions import InsecureRequestWarning
import time
import re

warnings.filterwarnings("ignore", category=InsecureRequestWarning)

aes_key = b'Yg&tc%DEuh6%Zc^8'
aes_iv = b'6oyZDr22E3ychjM%'

app = Flask(__name__)

template_data = bytes.fromhex('1a13323032352d31312d32362030313a35313a3238220966726565206669726528013a07312e3132332e314232416e64726f6964204f532039202f204150492d3238202850492f72656c2e636a772e32303232303531382e313134313333294a0848616e6468656c64520c4d544e2f537061636574656c5a045749464960800a68d00572033234307a2d7838362d3634205353453320535345342e3120535345342e32204156582041565832207c2032343030207c20348001e61e8a010f416472656e6f2028544d292036343092010d4f70656e474c20455320332e329a012b476f6f676c657c36323566373136662d393161372d343935622d396631362d303866653964336336353333a2010e3137362e32382e3133392e313835aa01026172b201203433303632343537393364653836646134323561353263616164663231656564ba010134c2010848616e6468656c64ca010d4f6e65506c7573204135303130ea014063363961653230386661643732373338623637346232383437623530613361316466613235643161313966616537343566633736616334613065343134633934f00101ca020c4d544e2f537061636574656cd2020457494649ca03203161633462383065636630343738613434323033626638666163363132306635e003b5ee02e8039a8002f003af13f80384078004a78f028804b5ee029004a78f029804b5ee02b00404c80401d2043d2f646174612f6170702f636f6d2e6474732e667265656669726574682d66705843537068495636644b43376a4c2d574f7952413d3d2f6c69622f61726de00401ea045f65363261623933353464386662356662303831646233333861636233333439317c2f646174612f6170702f636f6d2e6474732e667265656669726574682d66705843537068495636644b43376a4c2d574f7952413d3d2f626173652e61706bf00406f804018a050233329a050a32303139313139303236a80503b205094f70656e474c455332b805ff01c00504e005be7eea05093372645f7061727479f205704b717348543857393347646347335a6f7a454e6646775648746d377171316552554e6149444e67526f626f7a4942744c4f695943633459367a767670634943787a514632734f453463627974774c7334785a62526e70524d706d5752514b6d654f35766373386e51594268777148374bf805e7e4068806019006019a060134a2060134b2062213521146500e590349510e460900115843395f005b510f685b560a6107576d0f0366')

def encrypt_message(key, iv, plaintext):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_message = pad(plaintext, AES.block_size)
    return cipher.encrypt(padded_message)

def clean_token(token):
    jwt_pattern = r'eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+'
    match = re.search(jwt_pattern, token)
    if match:
        return match.group()
    return None

def GeT_GaReNa_ToKeN(uid, password, retries=3):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    headers = {
        "Host": "100067.connect.garena.com",
        "User-Agent": "GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close",
    }
    data = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": "",
        "client_id": "100067",
    }
    
    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, data=data, timeout=10)
            if response.status_code == 200:
                return response.json()
        except:
            if attempt == retries - 1:
                return None
            time.sleep(1)
    return None

def GeT_JwT_FrOm_MaJoRlOgIn(uid, password, retries=3):
    token_data = GeT_GaReNa_ToKeN(uid, password)
    if not token_data:
        return None
    
    if "access_token" not in token_data or "open_id" not in token_data:
        return None
    
    new_access_token = token_data['access_token']
    new_open_id = token_data['open_id']
    old_access_token = "c69ae208fad72738b674b2847b50a3a1dfa25d1a19fae745fc76ac4a0e414c94"
    old_open_id = "4306245793de86da425a52caadf21eed"
    
    modified_data = template_data.replace(old_open_id.encode(), new_open_id.encode())
    modified_data = modified_data.replace(old_access_token.encode(), new_access_token.encode())
    
    encrypted_data = encrypt_message(aes_key, aes_iv, modified_data)
    hex_encrypted_data = binascii.hexlify(encrypted_data).decode('utf-8')
    
    url = "https://loginbp.ggpolarbear.com/MajorLogin"
    headers = {
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/octet-stream",
        'Expect': "100-continue",
        'X-GA': "v1 1",
        'X-Unity-Version': "2018.4.11f1",
        'ReleaseVersion': "OB53"
    }
    edata = bytes.fromhex(hex_encrypted_data)
    
    for attempt in range(retries):
        try:
            response = requests.post(url, data=edata, headers=headers, verify=False, timeout=15)
            if response.status_code == 200:
                jwt = clean_token(response.text)
                if jwt:
                    return jwt
        except:
            pass
        time.sleep(1)
    
    return None

@app.route('/token', methods=['GET'])
def GeT_tOkEn_rEsPoNsE():
    uid = request.args.get('uid')
    password = request.args.get('password')
    
    if not uid or not password:
        return jsonify({"error": "Missing parameters: uid and password are required"}), 400
    
    jwt = GeT_JwT_FrOm_MaJoRlOgIn(uid, password)
    
    if not jwt:
        return jsonify({"error": "Failed to retrieve token"}), 500
    
    return jsonify({"token": jwt})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, threaded=True)