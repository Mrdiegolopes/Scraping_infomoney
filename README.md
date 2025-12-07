#  InfoMoney Economia Scraper

Um scraper desenvolvido em Python para coletar
notícias da seção **Mercados/Economia** do site **InfoMoney**.
O script realiza a extração de **títulos, links, datas e conteúdo
completo** das notícias, salva tudo em uma pasta organizada por data e
exporta os resultados em **Excel** e **TXT**.

------------------------------------------------------------------------

##  Funcionalidades

-    Busca automatizada de notícias na seção **Mercados** do
    InfoMoney.
-    Extração: título, link, data de publicação, data da
    coleta e corpo da notícia.
-    Limpeza e padronização do texto (remoção de ads, scripts,
    elementos inúteis).
-    Coleta inteligente com múltiplos seletores e fallback por links
    diretos.
-    Exportação automática para:
    -   **Excel (.xlsx)**
    -   **Texto (.txt)** contendo todo o conteúdo das matérias
-    Organização em pastas nomeadas com a data da coleta
-    Sem de duplicatas
-    Atraso automático entre requisições para evitar bloqueios

------------------------------------------------------------------------



A pasta `economia_infomoney_YYYY-MM-DD` é criada automaticamente a cada
execução.

------------------------------------------------------------------------

##  Como funciona

### 1. **Coleta de páginas**

O scraper acessa:

    https://www.infomoney.com.br/mercados/
    https://www.infomoney.com.br/mercados/page/2/
    https://www.infomoney.com.br/mercados/page/3/
    ...

Para cada página, identifica elementos HTML que podem conter notícias
utilizando padrões como:

-   `card`
-   `news`
-   `item`
-   `post`

### 2. **Fallback por links diretos**

Se não houver blocos padronizados, o scraper analisa **todos os links da
página**, filtrando:

-   URLs contendo `/noticias/` ou `/mercados/`
-   Títulos com mais de 30 caracteres
-   Remoção de links irrelevantes (tag, author, login etc.)

### 3. **Extração do conteúdo**

Tenta múltiplos seletores para encontrar o corpo da notícia:

``` python
conteudo_selectors = [
    'div.entry-content',
    'article .content',
    'div.article-content',
    'div.text',
    'div.content',
    'div[class*="content"]',
    'article'
]
```

Remove elementos indesejados:

-   script
-   style
-   anúncios
-   menus/header/footer

### 4. **Data da notícia**

Busca usando seletores como:

    time
    [class*="date"]
    [class*="data"]
    .post-date
    .article-date

------------------------------------------------------------------------

## Saída gerada

###  **Excel (`noticias_economia.xlsx`)**

Contém todas as notícias estruturadas com:

-   título
-   link
-   datas
-   conteúdo completo
-   tamanho do texto

###  **Arquivo TXT (`conteudos_completos.txt`)**

Formato:

    ============================================================
    NOTÍCIA 1: Título da matéria
    ============================================================
    URL: https://...
    Data publicação: ...
    Data coleta: ...
    Tamanho: XXXX caracteres

    CONTEÚDO:
    (texto limpo da notícia)

------------------------------------------------------------------------

## Fluxograma

<img width="832" height="1248" alt="fluxogramaa" src="https://github.com/user-attachments/assets/ee274fa2-309f-4f8d-92ba-bc54348de35e" />


##  Como executar

### 1. Instale as dependências:

``` bash
pip install requests beautifulsoup4 pandas openpyxl
```

### 2. Execute o script:

``` bash
python scraping.py
```

------------------------------------------------------------------------
<img width="832" height="1248" alt="fluxogramaa" src="https://github.com/user-attachments/assets/8471b1b9-b2b2-4a15-acbb-f9c3208aac2a" />

##  Observações Importantes

-   O scraping respeita intervalos (`sleep()`) para evitar bloqueios.
-   Mudanças no layout do InfoMoney podem quebrar seletores e exigir
    ajustes.\
-   Para buscar mais páginas, altere:

``` python
scraper.buscar_noticias_economia(paginas=2)
```

------------------------------------------------------------------------

## Melhorias ao curto prazo

-   Adicionar logs estruturados
-   Armazenar os dados em **SQLite ou PostgreSQL**
-   Paralelização para maior velocidade
-   Ferramentas de NLP para sumarização e análise
-   Escrita em banco de dados na nuvem

------------------------------------------------------------------------


