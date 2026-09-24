# Site União — versão institucional + painel administrativo

## Recursos
- Site responsivo PC/tablet/smartphone
- Início, Quem Somos, Downloads e Contato
- Hero para foto/vídeo, frota, história e segmentos
- Painel `/admin/login`
- Login protegido
- SQLite
- CRUD de vendedores
- CRUD de regiões
- Upload de catálogo, logo, fotos e mídia
- Mapa Leaflet/OpenStreetMap com vendedores por UF
- WhatsApp dos vendedores

## Executar no Windows
```powershell
cd site-uniao
py -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Abra `http://127.0.0.1:5000`.

Login inicial: `admin@uniao.local` / `admin123` — troque a senha antes de publicar.

## Produção
Defina `SECRET_KEY` como variável de ambiente e troque a credencial inicial. Para hospedagem, recomenda-se PostgreSQL e servidor WSGI (Gunicorn/Waitress), HTTPS e backup do banco.
