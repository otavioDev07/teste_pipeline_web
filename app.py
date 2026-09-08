from flask import Flask, jsonify, request, render_template, send_from_directory
import os
from werkzeug.utils import secure_filename
import subprocess
import requests

app = Flask(__name__)

TMP_FOLDER = './tmp_uploads'
RESULT_FOLDER = './tmp_recortados'
if not os.path.exists(TMP_FOLDER): os.makedirs(TMP_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

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
        
        print(f"\n--- DEBUG DA IMAGEM: {nome_seguro} ---")
        print("SAÍDA NORMAL (STDOUT):")
        print(saida)
        print("ERROS (STDERR):")
        print(processo.stderr)
        print("--------------------------------------\n")

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

@app.route('/imagem/<tipo>/<nome_arquivo>')
def servir_imagem(tipo, nome_arquivo):
    pasta = RESULT_FOLDER if tipo == 'aceita' else TMP_FOLDER 
    return send_from_directory(pasta, nome_arquivo)

if __name__ == '__main__':
    app.run(debug=True)