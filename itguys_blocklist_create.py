import requests
import os
import subprocess
import re
import socket
import concurrent.futures

# Passo 2: Definir os Links do GitHub
github_links = [
    'https://raw.githubusercontent.com/PolishFiltersTeam/KADhosts/master/KADhosts.txt',
    'https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.Spam/hosts',
    'https://v.firebog.net/hosts/static/w3kbl.txt',
    'https://raw.githubusercontent.com/matomo-org/referrer-spam-blacklist/master/spammers.txt',
    'https://someonewhocares.org/hosts/zero/hosts',
    'https://raw.githubusercontent.com/VeleSila/yhosts/master/hosts',
    'https://winhelp2002.mvps.org/hosts.txt',
    'https://v.firebog.net/hosts/neohostsbasic.txt',
    'https://raw.githubusercontent.com/RooneyMcNibNug/pihole-stuff/master/SNAFU.txt',
    'https://paulgb.github.io/BarbBlock/blacklists/hosts-file.txt',
    'https://adaway.org/hosts.txt',
    'https://v.firebog.net/hosts/AdguardDNS.txt',
    'https://v.firebog.net/hosts/Admiral.txt',
    'https://raw.githubusercontent.com/anudeepND/blacklist/master/adservers.txt',
    'https://s3.amazonaws.com/lists.disconnect.me/simple_ad.txt',
    'https://v.firebog.net/hosts/Easylist.txt',
    'https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&showintro=0&mimetype=plaintext',
    'https://raw.githubusercontent.com/FadeMind/hosts.extras/master/UncheckyAds/hosts',
    'https://raw.githubusercontent.com/bigdargon/hostsVN/master/hosts',
    'https://raw.githubusercontent.com/jdlingyu/ad-wars/master/hosts',
    'https://v.firebog.net/hosts/Easyprivacy.txt',
    'https://v.firebog.net/hosts/Prigent-Ads.txt',
    'https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.2o7Net/hosts',
    'https://raw.githubusercontent.com/crazy-max/WindowsSpyBlocker/master/data/hosts/spy.txt',
    'https://hostfiles.frogeye.fr/firstparty-trackers-hosts.txt',
    'https://www.github.developerdan.com/hosts/lists/ads-and-tracking-extended.txt',
    'https://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/android-tracking.txt',
    'https://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/SmartTV.txt',
    'https://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/AmazonFireTV.txt',
    'https://gitlab.com/quidsup/notrack-blocklists/raw/master/notrack-blocklist.txt',
    'https://raw.githubusercontent.com/DandelionSprout/adfilt/master/Alternate%20versions%20Anti-Malware%20List/AntiMalwareHosts.txt',
    'https://osint.digitalside.it/Threat-Intel/lists/latestdomains.txt',
    'https://s3.amazonaws.com/lists.disconnect.me/simple_malvertising.txt',
    'https://v.firebog.net/hosts/Prigent-Crypto.txt',
    'https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.Risk/hosts',
    'https://bitbucket.org/ethanr/dns-blacklists/raw/8575c9f96e5b4a1308f2f12394abd86d0927a4a0/bad_lists/Mandiant_APT1_Report_Appendix_D.txt',
    'https://phishing.army/download/phishing_army_blocklist_extended.txt',
    'https://gitlab.com/quidsup/notrack-blocklists/raw/master/notrack-malware.txt',
    'https://v.firebog.net/hosts/RPiList-Malware.txt',
    'https://v.firebog.net/hosts/RPiList-Phishing.txt',
    'https://raw.githubusercontent.com/Spam404/lists/master/main-blacklist.txt',
    'https://raw.githubusercontent.com/AssoEchap/stalkerware-indicators/master/generated/hosts',
    'https://urlhaus.abuse.ch/downloads/hostfile/',
    'https://malware-filter.gitlab.io/malware-filter/phishing-filter-hosts.txt',
    'https://v.firebog.net/hosts/Prigent-Malware.txt',
    'https://www.github.developerdan.com/hosts/lists/ads-and-tracking-extended.txt',
    'https://www.github.developerdan.com/hosts/lists/hate-and-junk-extended.txt',
    'https://www.github.developerdan.com/hosts/lists/tracking-aggressive-extended.txt',
    'https://dbl.oisd.nl/'
]

# Função para excluir arquivos com nomes que começam com até três dígitos
def delete_numeric_files():
    for file in os.listdir():
        if re.match(r'^\d{1,3}_', file):
            os.remove(file)
            print(f"Arquivo {file} removido.")

# Função para baixar e salvar os arquivos com um número no início
def download_and_save_file(link, index):
    try:
        response = requests.get(link)
        response.raise_for_status()  # Verificar se houve erro no download
        # Extrair a extensão do arquivo
        ext = os.path.splitext(link)[1]

        # Obter um nome de arquivo válido usando expressões regulares
        file_name = re.sub(r'[\/:*?"<>|]', '_', os.path.basename(link))
        file_name = f"{index:03}_{file_name}"

        # Adicionar a extensão ao nome do arquivo
        file_name_with_ext = f"{file_name}{ext}"

        # Verificar se o nome do arquivo é válido
        if not os.path.isabs(file_name_with_ext) and not file_name_with_ext.startswith(".."):
            with open(file_name_with_ext, 'wb') as file:
                file.write(response.content)
            print(f"Arquivo {file_name_with_ext} baixado com sucesso.")
        else:
            print(f"Falha ao gerar nome de arquivo válido para {link}.")
    except (requests.exceptions.RequestException, OSError) as e:
        print(f"Falha ao baixar o arquivo de {link}: {e}")

# Função para processar os IPs e remover duplicatas inúteis
def process_ips(file_names):
    all_ips = set()
    for file_name in file_names:
        with open(file_name, 'r', encoding='utf-8', errors='ignore') as file:
            lines = file.readlines()
            for line in lines:
                ip = line.strip()
                all_ips.add(ip)
    return all_ips

# Função para criar o arquivo final "hosts" para o Windows
def create_final_hosts_file(ip_set):
    final_file_name = "999_lista_itguys.txt"
    with open(final_file_name, 'w', encoding='utf-8') as final_file:
        final_file.write("# Arquivo de hosts personalizado\n")
        final_file.write("# Qualquer alteração feita aqui afetará o redirecionamento de domínios\n")
        for ip in ip_set:
            final_file.write(f"{ip}\n")
    print(f"Arquivo final {final_file_name} criado com sucesso.")

# Passo 3: Chamar as Funções
if __name__ == "__main__":
    delete_numeric_files()  # Excluir arquivos existentes antes de começar

    # Download paralelo dos arquivos
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for index, link in enumerate(github_links, start=1):
            executor.submit(download_and_save_file, link, index)

    # Obter a lista de nomes de arquivo baixados
    txt_files = [file for file in os.listdir() if file.endswith(".txt")]

    unique_ips = process_ips(txt_files)

    create_final_hosts_file(unique_ips)