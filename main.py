import tkinter as tk
from tkinter import filedialog, messagebox
import requests
import os
import shutil
import time
import json

# ATENÇÃO: ESTE SCRIPT NÃO CONTÉM NENHUMA CREDENCIAL REAL.
# INSIRA SUAS PRÓPRIAS CREDENCIAIS PARA USO PESSOAL OU PROFISSIONAL.

def login():
    url = 'https://login.windows.net/common/oauth2/token/'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    body = {
        "grant_type": "YOUR_CLIENT_ID_HERE",
        "resource": "YOUR_CLIENT_ID_HERE",
        "scope": "YOUR_CLIENT_ID_HERE",
        "client_id": "YOUR_CLIENT_ID_HERE",
        "client_secret": "YOUR_CLIENT_ID_HERE",
        "username": "YOUR_CLIENT_ID_HERE",
        "password": "YOUR_CLIENT_ID_HERE"       
    }

    response = requests.post(url, headers=headers, data=body)

    if response.status_code == 200:
        token = response.json().get('access_token')
        print("Login realizado com sucesso.")
        return token
    else:
        print("Falha no login.")
        print(response.status_code, response.text)
        return None

def get_workspaces(token):
    url = 'https://api.powerbi.com/v1.0/myorg/groups/'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    return response.json().get('value', []) if response.status_code == 200 else []

def get_datasets(token, workspace_id):
    url = f'https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    return response.json().get('value', []) if response.status_code == 200 else []

def get_parameters(token, workspace_id, dataset_id):
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/parameters"
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("value", [])
    return []

    
def set_parameters(token, workspace_id, dataset_id, parametros):
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/Default.UpdateParameters"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    update_details = []
    for parametro in parametros:
        update_details.append({
            "name": parametro['name'],
            "newValue": parametro['currentValue']  # Captura valor do Dataset Selecionado
        })

    payload = {
        "updateDetails": update_details
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code in [200, 204]:
        return True
    else:
        print(f"\nErro ao atualizar parâmetros:")
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text}")
        print(f"Payload enviado: {json.dumps(payload, indent=2)}")
        return False


def refresh_dataset(token, workspace_id, dataset_id):
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/refreshes"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers)
    return response.status_code == 202

def publicar(token, workspace_id, dataset_ids, pbix_path):
    # Armazenar valores de servidor e banco de dados
    parametros = []
    for dataset_id in dataset_ids:
        dataset_nome = next((d['name'] for d in get_datasets(token, workspace_id) if d['id'] == dataset_id), None)
        if not dataset_nome:
            return False

        novo_pbix_path = os.path.join(os.path.dirname(pbix_path), f"{dataset_nome}.pbix")
        shutil.copy(pbix_path, novo_pbix_path)

        parametros_originais = get_parameters(token, workspace_id, dataset_id)
        parametros.append(parametros_originais)
        print(f"Parâmetros capturados do dataset original {dataset_nome}: {parametros_originais}")

        url = f'https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/imports?datasetDisplayName={dataset_nome}&nameConflict=Overwrite'
        headers = {'Authorization': f'Bearer {token}'}

        with open(novo_pbix_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, headers=headers, files=files)

        if response.status_code not in [200, 201, 202]:
            print("Erro ao publicar:", response.status_code, response.text)
            return False

        print(f"PBIX para {dataset_nome} enviado com sucesso. Aguardando processamento...")

        novo_dataset_id = None
        for _ in range(20):
            time.sleep(3)
            novos_datasets = get_datasets(token, workspace_id)
            for d in novos_datasets:
                if d['name'] == dataset_nome:
                    novo_dataset_id = d['id']
                    break
            if novo_dataset_id:
                break

        if not novo_dataset_id:
            print(f"Erro: Novo dataset {dataset_nome} não encontrado após publicação.")
            return False

        for _ in range(10):
            novos_parametros = get_parameters(token, workspace_id, novo_dataset_id)
            if novos_parametros:
                break
            time.sleep(3)

        if not novos_parametros:
            print("Erro: Parâmetros do novo dataset não disponíveis.")
            return False

        # Atualiza os parâmetros com os valores originais do Dataset
        sucesso_param = set_parameters(token, workspace_id, novo_dataset_id, parametros_originais)
        if sucesso_param:
            print(f"Parâmetros atualizados com sucesso no novo dataset {dataset_nome}.")
        else:
            print(f"Falha ao atualizar os parâmetros no novo dataset {dataset_nome}.")
            return False

        # Inicia atualizacção do Dataset
        sucesso_refresh = refresh_dataset(token, workspace_id, novo_dataset_id)
        if sucesso_refresh:
            print(f"Atualização do novo dataset {dataset_nome} iniciada com sucesso.")
        else:
            print(f"Erro ao iniciar atualização do novo dataset {dataset_nome}.")

    return True


class PowerBIPublisherApp:
    def __init__(self, root): #Parte Visual do codigo
        self.root = root
        self.root.title("Publicar PBIX no Power BI")

        self.token = login()
        if not self.token:
            messagebox.showerror("Erro", "Falha no login. Verifique o client_id.")
            root.quit()

        self.workspace_var = tk.StringVar()
        self.dataset_vars = []
        self.pbix_path = ""

        main_frame = tk.Frame(root)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True)

        tk.Label(left_frame, text="Selecione o Workspace:").pack(anchor="w")
        self.workspace_menu = tk.OptionMenu(left_frame, self.workspace_var, "")
        self.workspace_menu.pack(fill="x")

        tk.Label(left_frame, text="Selecione os Datasets:").pack(anchor="w")
        self.datasets_frame = tk.Frame(left_frame)
        self.datasets_frame.pack(fill="both", expand=True)

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="right", fill="y", padx=(20, 0))

        tk.Button(right_frame, text="Buscar Workspaces", command=self.load_workspaces).pack(fill="x", pady=2)
        tk.Button(right_frame, text="Buscar Datasets", command=self.load_datasets).pack(fill="x", pady=2)
        tk.Button(right_frame, text="Selecionar Arquivo PBIX", command=self.select_pbix).pack(fill="x", pady=2)
        tk.Button(right_frame, text="Selecionar Todos os Datasets", command=self.select_all_datasets).pack(fill="x", pady=2)
        tk.Button(right_frame, text="Publicar", command=self.publicar_pbix).pack(fill="x", pady=2)

    # os métodos:
    def load_workspaces(self):
        workspaces = get_workspaces(self.token)
        if workspaces:
            self.workspace_options = {w['name']: w['id'] for w in workspaces}
            menu = self.workspace_menu['menu']
            menu.delete(0, 'end')
            for name in self.workspace_options:
                menu.add_command(label=name, command=lambda v=name: self.workspace_var.set(v))

    def load_datasets(self):
        wid = self.workspace_options.get(self.workspace_var.get())
        datasets = get_datasets(self.token, wid)
        if datasets:
            for widget in self.datasets_frame.winfo_children():
                widget.destroy()
            self.dataset_vars = []

            for dataset in datasets:
                var = tk.BooleanVar()
                checkbox = tk.Checkbutton(self.datasets_frame, text=dataset['name'], variable=var)
                checkbox.pack(anchor="w")
                self.dataset_vars.append((dataset['id'], var))

    def select_pbix(self):
        path = filedialog.askopenfilename(filetypes=[("PBIX files", "*.pbix")])
        if path:
            self.pbix_path = path
            messagebox.showinfo("Selecionado", f"Arquivo: {os.path.basename(path)}")

    def select_all_datasets(self):
        for _, var in self.dataset_vars:
            var.set(True)

    def publicar_pbix(self):
        wid = self.workspace_options.get(self.workspace_var.get())
        if not (wid and self.pbix_path):
            messagebox.showwarning("Faltando", "Todos os campos devem ser preenchidos.")
            return

        dataset_ids = [dataset_id for dataset_id, var in self.dataset_vars if var.get()]
        if not dataset_ids:
            messagebox.showwarning("Faltando", "Selecione pelo menos um dataset.")
            return

        sucesso = publicar(self.token, wid, dataset_ids, self.pbix_path)
        if sucesso:
            messagebox.showinfo("Sucesso", "PBIX publicado, parâmetros copiados e dataset(s) atualizado(s)!")
        else:
            messagebox.showerror("Erro", "Falha ao publicar o PBIX.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PowerBIPublisherApp(root)
    root.mainloop()
