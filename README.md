# CpuMeter

CpuMeter é um pequeno monitor de CPU/RAM para Windows desenvolvido em Python usando Tkinter e psutil.

## Recursos

- Mostra o uso atual de CPU em um marcador circular.
- Exibe o uso de RAM em texto.
- Janela sem borda sempre no topo.
- Arraste com o botão esquerdo do mouse.
- Fecha com duplo-clique.
- Vermelho quando valor acima de 90%.
- Aumenta e diminui o tamanho da janela usando scroll do mouse.

## Requisitos

- Python 3.8+ (ou versão compatível com Tkinter)
- Biblioteca `psutil`

## Instalação

1. Instale o Python se ainda não estiver instalado.
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Uso

Execute o aplicativo:

```bash

python main.py
```
## Para gerar o executável para windows
 ```bash
 python -m PyInstaller --onefile --noconsole -n CpuRamMeter main.py
```

## Observações

- O recurso de transparência de fundo funciona melhor no Windows.
- A janela não possui borda para um visual compacto.

## Licença

Use como preferir. Este projeto não inclui uma licença específica.


# EXE

## Versões Disponíveis

| Versão | Download |
| :--- | :--- |
| **1.0** | [CpuRamMeter.exe](https://github.com/schimin/cpu_ram_meter/blob/main/dist/CpuRamMeter.exe) |
| **1.2** | [CpuRamMeter-1.2.exe](https://github.com/schimin/cpu_ram_meter/blob/main/dist/CpuRamMeter-1.2.exe) |

.