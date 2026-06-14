#!/usr/bin/env fish
# chmod +x setup.fish

echo "Criando ambiente virtual..."
python3 -m venv .venv


echo "Instalando dependências..."
.venv/bin/pip install -r requirements.txt

echo ""
echo "Ambiente criado com sucesso!"
echo "Para ativar:"
echo "source .venv/bin/activate.fish"