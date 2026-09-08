from flask import Flask, jsonify, request
import os
from werkzeug.utils import secure_filename
import subprocess
import requests

app = Flask(__name__)

TMP_FOLDER = './tmp_uploads'
RESULT_FOLDER = './tmp_recortados'
if not os.path.exists(TMP_FOLDER): os.makedirs(TMP_FOLDER)

@app.route('/upload/', methods=['POST'])
def processar_lote():
    webhook = request.form.get('webhook_url')
    token = request.form.get('token')
    imgs = request.files.getlist('imagens')

    aceitas = []
    negadas = []

    for img in imgs:
        nome_seguro = secure_filename(img.filename)
        caminho = os.path.join(TMP_FOLDER, nome_seguro)
        img.save(caminho)

        processo = subprocess.run(["./pipeline.sh", caminho], capture_output=True, text=True)
        saida = processo.stdout

        if '[5/5] Executando recorte' in saida:
            aceitas.append(nome_seguro)

            if webhook:
                caminho_recortado = os.path.join(RESULT_FOLDER, nome_seguro)
                
                if os.path.exists(caminho_recortado):
                    with open(caminho_recortado, 'rb') as f:
                        arquivos = {'file':(nome_seguro, f, 'image/jpeg')}
                        dados = {'upload_token': token}
                        requests.post(webhook, files=arquivos, data=dados)
        else:
            negadas.append(nome_seguro)

    return jsonify({"status": "sucesso", "arquivos_recebidos": len(imgs), "aceitas":aceitas, "negadas":negadas})


if __name__ == '__main__':
    app.run(debug=True)