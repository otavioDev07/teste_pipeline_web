from flask import Flask, jsonify, request, render_template, send_from_directory
import os
from werkzeug.utils import secure_filename
import subprocess
import requests
from PIL import Image 

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
        try:
            with Image.open(caminho) as imagem_pil:
                max_size = (1200, 1200) # Dimensão máxima segura
                imagem_pil.thumbnail(max_size, Image.Resampling.LANCZOS)
                # Salva por cima do arquivo original já otimizado e mais leve
                imagem_pil.save(caminho, optimize=True, quality=85)
        except Exception as e:
            print(f"Erro ao redimensionar {nome_seguro}: {e}")

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