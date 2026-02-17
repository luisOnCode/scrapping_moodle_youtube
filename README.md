# 🤖 Automação Moodle & YouTube (Gerador de JSON)

## 🎯 O que este projeto resolve?
Alimentar plataformas EAD (como o Moodle) com dezenas de vídeos do YouTube pode ser um processo extremamente manual, repetitivo e sujeito a erros humanos. 

Este projeto resolve essa dor extraindo automaticamente os dados de uma playlist do YouTube e pareando-os com os módulos de atividades (H5P) previamente criados no Moodle. O script lê o código-fonte (HTML) de ambas as páginas e cruza as informações, gerando um arquivo JSON padronizado. Esse JSON serve como base confiável para robôs de automação (como o Playwright) realizarem o preenchimento final na plataforma.

## 🔒 Segurança e Privacidade de Dados
Para garantir a segurança das informações (links privados, dados do curso, IDs internos), **os arquivos HTML extraídos e o JSON gerado não são comitados neste repositório**. 

Eles estão mapeados no nosso `.gitignore`:
- `**/*mapeadas.json`
- `**/*mdl.html`
- `**/*yt.html`

## 🚀 Como configurar o ambiente (Setup)

Este projeto utiliza Python. Para não conflitar com outras bibliotecas da sua máquina, recomendamos o uso de um Ambiente Virtual (venv).

1. **Crie a venv:**
   No terminal, dentro da pasta do projeto, rode:
   `python -m venv .venv`

2. **Ative a venv:**
   - **Linux/macOS:** `source .venv/bin/activate`
   - **Windows:** `.venv\Scripts\activate`

3. **Instale as dependências:**
   Com a venv ativada, instale o interpretador de HTML (BeautifulSoup) e o Playwright:
   `pip install beautifulsoup4 playwright`

## 🛠️ Como utilizar o Gerador de JSON

Para que o script funcione, você precisa extrair manualmente o HTML da página do Moodle e da playlist do YouTube e colocá-los na raiz do projeto.

### 1. Preparando os arquivos
- **Moodle:** Acesse a página de edição do curso, copie o HTML (via *Inspect/Elements*) da seção onde estão as atividades e salve o arquivo terminando em `.mdl.html` (ex: `modulo_css.mdl.html`).
- **YouTube:** Acesse a página da playlist, copie o HTML que envolve os vídeos e salve o arquivo terminando em `.yt.html` (ex: `playlist_css.yt.html`).

💡 **Dica de Ouro (Playlists Invertidas):** Se a playlist do YouTube estiver com a ordem do último vídeo para o primeiro, basta adicionar a palavra `flip` no nome do arquivo (ex: `playlist_css.flip.yt.html`). O script detectará isso e inverterá a lista automaticamente para parear corretamente com o Moodle!

### 2. Rodando o Script
Com os arquivos na pasta e a `venv` ativada, execute:
`python gerador_json.py`

### 3. Resultado
O script fará uma validação rígida. Se a quantidade de vídeos do YouTube for exatamente igual à quantidade de atividades do Moodle, ele gerará o arquivo `atividades_mapeadas.json` na raiz do projeto, pronto para ser consumido pela automação!