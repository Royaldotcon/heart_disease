from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from web3 import Web3 
import os
import json

app = Flask(__name__)


WEB3_PROVIDER_URL = os.getenv("WEB3_PROVIDER_URL", "http://127.0.0.1:8545") 
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "0xYourDeployedContractAddressHere") 
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "0xYourPrivateKeyHere") 
CONTRACT_ABI_PATH = "abi/HeartDiseaseOracle.json"
w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URL))

if not w3.is_connected():
    print("Failed to connect to Web3 provider!")
else:
    print(f"Successfully connected to Web3 provider: {WEB3_PROVIDER_URL}")

try:
    with open(CONTRACT_ABI_PATH, 'r') as f:
        contract_abi = json.load(f)
    heart_disease_oracle = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)
    print("Smart contract loaded successfully.")
except FileNotFoundError:
    print(f"Error: Contract ABI file not found at {CONTRACT_ABI_PATH}")
    heart_disease_oracle = None
except Exception as e:
    print(f"Error loading smart contract: {e}")
    heart_disease_oracle = None


try:
    model = pickle.load(open("model/heart_model.pkl", "rb"))
except:
    df = pd.read_csv("dataset/dataset.csv")
    X = df.drop("target", axis=1)
    y = df["target"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    pickle.dump(model, open("model/heart_model.pkl", "wb"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = [float(request.form[key]) for key in request.form]
        prediction_value = model.predict([data])[0]
        result_text = "Heart Disease Detected 💔" if prediction_value == 1 else "No Heart Disease ❤️"

        if heart_disease_oracle and w3.is_connected():
            try:
              
                account = w3.eth.account.from_key(PRIVATE_KEY)
                w3.eth.default_account = account.address

                
                transaction = heart_disease_oracle.functions.requestPredictionProcessing(result_text).build_transaction({
                    'from': account.address,
                    'nonce': w3.eth.get_transaction_count(account.address),
                    'gasPrice': w3.eth.gas_price 
                })

                signed_txn = w3.eth.account.sign_transaction(transaction, private_key=PRIVATE_KEY)

                tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

                print(f"Transaction sent to blockchain. Tx Hash: {tx_hash.hex()}")
                print(f"Transaction Receipt: {tx_receipt}")

         
                return jsonify({
                    "result": result_text,
                    "blockchain_tx_hash": tx_hash.hex(),
                    "message": "Prediction processed and request sent to blockchain via Chainlink Functions."
                })

            except Exception as chainlink_e:
                print(f"Error interacting with Chainlink/Blockchain: {chainlink_e}")
                return jsonify({"result": result_text, "error": f"Failed to send prediction to blockchain: {str(chainlink_e)}"})
        else:
            return jsonify({"result": result_text, "message": "Blockchain interaction skipped (contract not loaded or not connected)."})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)