import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os
import re

class InfoMoneyEconomiaScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def buscar_noticias_economia(self, paginas=3):
        #busca noticias na seção economia 
        base_url = "https://www.infomoney.com.br/mercados/"
        print(f"Buscando notícias de Economia/Mercados...")

        todas_noticias = []

        for pagina in range(1, paginas + 1):
            if pagina == 1:
                url = base_url
            else:
                url = f"{base_url}page/{pagina}/"

            print(f"\n Página {pagina}: {url}")

            noticias_pagina = self._extrair_noticias_pagina(url)
            todas_noticias.extend(noticias_pagina)

            if not noticias_pagina:
                print(" Nenhuma notícia encontrada nesta página")
                break

            time.sleep(2)

        print(f"\n Total encontrado: {len(todas_noticias)} notícias")
        return todas_noticias

    def _extrair_noticias_pagina(self, url):
        #extrai notícias de uma página especifica 
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            noticias = []

            # buscar por elementos de noticia comuns
            elementos_noticia = soup.find_all('div', class_=re.compile(r'card|news|item|post'))

            print(f" Encontrados {len(elementos_noticia)} elementos possíveis")

            for elemento in elementos_noticia:
                noticia = self._extrair_dados_elemento(elemento)
                if noticia and noticia['titulo'] and noticia['link']:
                    # verificação de duplicata
                    if not any(n['link'] == noticia['link'] for n in noticias):
                        noticias.append(noticia)

            # buscar por links de noticias
            if not noticias:
                noticias = self._buscar_por_links_diretos(soup)

            print(f" Notícias válidas encontradas: {len(noticias)}")
            return noticias

        except Exception as e:
            print(f" Erro ao acessar página: {e}")
            return []

    def _buscar_por_links_diretos(self, soup):
       #busca notícias analisando links diretamente
        noticias = []

        # encontra todos os links que podem ser de notícias
        links = soup.find_all('a', href=True)

        for link in links:
            href = link['href'] # url do link
            titulo = link.get_text(strip=True) # texto visivel do link

            # Filtragem para links de noticias de economia/mercados
            if (href and
                any(termo in href for termo in ['/noticias/', '/mercados/']) and
                titulo and len(titulo) > 30 and
                not any(x in href for x in ['category', 'tag', 'author', '?page=', '#']) and
                not any(x in titulo.lower() for x in ['voltar', 'menu', 'login', 'cadastre'])):

                link_completo = self._completar_url(href)

                if not any(link_completo == n['link'] for n in noticias):
                    noticias.append({
                        'titulo': titulo[:300],
                        'link': link_completo,
                        'data_coleta': datetime.now()
                    })

        return noticias[:20] 

    def _extrair_dados_elemento(self, elemento):
        # extrai dados de um elemento de noticia
        try:
            # tentando encontrar titulo
            titulo = ""
            for tag in ['h2', 'h3', 'h4']:
                titulo_element = elemento.find(tag)
                if titulo_element:
                    titulo = titulo_element.get_text(strip=True)
                    if titulo:
                        break

            # se nao foi encontrao tenta no link ou no próprio elemento
            if not titulo:
                link_element = elemento.find('a')
                if link_element:
                    titulo = link_element.get_text(strip=True)
                else:
                    titulo = elemento.get_text(strip=True)

            # encontra o link
            link = ""
            link_element = elemento.find('a', href=True)
            if link_element:
                href = link_element['href']
                if any(termo in href for termo in ['/noticias/', '/mercados/']):
                    link = self._completar_url(href)

            if not titulo or not link or len(titulo) < 20:
                return None

            return {
                'titulo': titulo[:300],
                'link': link,
                'data_coleta': datetime.now()
            }

        except Exception as e:
            return None

    def extrair_conteudo_completo(self, noticias):
        #extrai o conteudo completo de cada pagina
        print(f"\n Extraindo conteúdo de {len(noticias)} notícias...")

        for i, noticia in enumerate(noticias, 1):
            print(f"[{i}/{len(noticias)}]  {noticia['titulo'][:80]}...")

            conteudo, data_publicacao = self._extrair_texto_noticia(noticia['link'])
            #vai ate a pag da noticia, faz parsing do html, procura o text princial
            noticia['conteudo'] = conteudo
            noticia['data_publicacao'] = data_publicacao
            noticia['tamanho_conteudo'] = len(conteudo)

            #progresso
            if conteudo and len(conteudo) > 100:
                print(f" conteúdo: {len(conteudo)} caracteres")
            else:
                print(f" conteúdo curto ou vazio")

            time.sleep(3)  

        return noticias

    def _extrair_texto_noticia(self, url):
        #extrai o texto completo e data da notícia
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # extrai data de publicação
            data_publicacao = self._extrair_data(soup)

            # extrai conteúdo
            conteudo = ""

            # tentativa de encontrar o conteúdo principal
            conteudo_selectors = [
                'div.entry-content',
                'article .content',
                'div.article-content',
                'div.text',
                'div.content',
                'div[class*="content"]',
                'article'
            ]

            for selector in conteudo_selectors:
                elemento = soup.select_one(selector)
                if elemento:
                    # removendo elementos indesejados
                    for tag in elemento.select('script, style, nav, header, footer, aside, .ad, [class*="ad"]'):
                        tag.decompose()

                    texto = elemento.get_text(separator='\n', strip=True)
                    linhas = [linha.strip() for linha in texto.split('\n') if linha.strip()]
                    conteudo = '\n'.join(linhas)

                    if len(conteudo) > 100:
                        break

            return conteudo, data_publicacao

        except Exception as e:
            return f"erro ao extrair: {str(e)}", "aata não encontrada"

    def _extrair_data(self, soup):
        # extrai data de publicação
        try:
            # procura por elemento data
            data_selectors = [
                'time',
                '[class*="date"]',
                '[class*="data"]',
                '.post-date',
                '.article-date'
            ]

            for selector in data_selectors:
                elemento = soup.select_one(selector)
                if elemento:
                    data_texto = elemento.get_text(strip=True)
                    if data_texto:
                        return data_texto

            return "data não encontrada"
        except:
            return "data não encontrada"

    def _completar_url(self, url):
        
        if url.startswith('http'):
            return url
        else:
            return 'https://www.infomoney.com.br' + url

    def salvar_resultados(self, noticias):
        
        if not noticias:
            print(" Nenhuma notícia para salvar")
            return

        # CRIANDO PASTA COM DATA
        pasta = f"economia_infomoney_{datetime.now().strftime('%Y-%m-%d')}"
        os.makedirs(pasta, exist_ok=True)

        # SALVA EM EXCEL
        df = pd.DataFrame(noticias)
        excel_path = os.path.join(pasta, 'noticias_economia.xlsx')
        df.to_excel(excel_path, index=False, engine='openpyxl')

        # SALVA EM TXT
        txt_path = os.path.join(pasta, 'conteudos_completos.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(" Noticas de economia INFOMONEY \n\n")
            for i, noticia in enumerate(noticias, 1):
                f.write(f"{"="*60}\n")
                f.write(f"NOTÍCIA {i}: {noticia['titulo']}\n")
                f.write(f"{"="*60}\n")
                f.write(f"URL: {noticia['link']}\n")
                f.write(f"Data publicação: {noticia.get('data_publicacao', 'N/A')}\n")
                f.write(f"Data coleta: {noticia['data_coleta'].strftime('%d/%m/%Y %H:%M')}\n")
                f.write(f"Tamanho: {noticia.get('tamanho_conteudo', 0)} caracteres\n\n")
                f.write(f"CONTEÚDO:\n{noticia.get('conteudo', 'N/A')}\n\n\n")

        print(f"\n resultados salvos:")
        print(f" Excel: {excel_path}")
        print(f" TXT com conteúdos: {txt_path}")
        print(f" Pasta: {pasta}")

        # estatisticas
        noticias_com_conteudo = [n for n in noticias if n.get('tamanho_conteudo', 0) > 100]
        print(f"\n estatisticas :")
        print(f" Notícias com conteúdo válido: {len(noticias_com_conteudo)}/{len(noticias)}")
        if noticias_com_conteudo:
            tamanhos = [n['tamanho_conteudo'] for n in noticias_com_conteudo]
            print(f" media de caracteres: {sum(tamanhos)/len(tamanhos):.0f}")
            

def main():
    scraper = InfoMoneyEconomiaScraper()

    print("=" * 60)
    print("      SCRAPER ECONOMIA - INFO MONEY")
    print("=" * 60)

    # busca noticias de economia
    noticias = scraper.buscar_noticias_economia(paginas=2)

    if noticias:
        # extrai o conteudo completo
        noticias_completas = scraper.extrair_conteudo_completo(noticias)

        #salva os resultadoros 
        scraper.salvar_resultados(noticias_completas)

    else:
        print(" nenhuma noticia de economia encontrada.")

if __name__ == "__main__":
    main()