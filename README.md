# 📡 Software Serial

Leitura e envio de pacotes de dados via comunicação serial, com suporte a simulação e geração de relatórios.

Inicialmente desenvolvido para interagir com módulos **XBee**, este projeto permite:

- 📥 Captura de pacotes em hexadecimal
- 📤 Transmissão de dados via porta serial
- 🧪 Simulação de dados para testes
- 📊 Geração de relatórios a partir dos dados coletados

---

## 🧩 Estrutura do Projeto

| Arquivo/Pasta             | Descrição                                                               |
|--------------------------|-------------------------------------------------------------------------|
| `main.py`                | Arquivo principal para iniciar a aplicação                              |
| `XBeeDataViewer.py`      | Interface gráfica para visualização dos dados                           |
| `RealXBeeData.py`        | Comunicação com o dispositivo XBee                                      |
| `envia.py`               | Script para envio de dados via serial                                   |
| `data_log1.txt`          | Exemplo de log de dados coletados                                       |
| `Software Serial.pdf`    | Documento explicativo sobre o funcionamento do software                 |
| `SoftwareSerial/`        | Diretório contendo módulos auxiliares                                   |
| `__pycache__/`           | Arquivos compilados automaticamente pelo Python                         |

---

## 🚀 Como Usar

1. Clone o repositório:

   ```bash
   git clone https://github.com/gilsonfiho/Serial.git
