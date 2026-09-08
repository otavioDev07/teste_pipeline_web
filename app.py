from flask import Flask, jsonify, request
import os
from werkzeug.utils import secure_filename
import subprocess

app = Flask(__name__)

TMP_FOLDER = './tmp_uploads'
if not os.path.exists(TMP_FOLDER): os.makedirs(TMP_FOLDER)

@app.route('/upload/', methods=['POST'])
def processar_lote():
    webhook = request.form.get('webhook_url')
    token = request.form.get('token')
    imgs = request.files.getlist('imagens')

    for img in imgs:
        nome_seguro = secure_filename(img.filename)
        caminho = os.path.join(TMP_FOLDER, nome_seguro)
        img.save(caminho)

    return jsonify({"status": "sucesso", "arquivos_recebidos": len(imgs)})


if __name__ == '__main__':
    app.run(debug=True)