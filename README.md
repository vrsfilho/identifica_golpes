# Detector de Golpes

Sistema inteligente que utiliza IA para analisar mensagens e identificar possíveis tentativas de golpes financeiros, fornecendo alertas e orientações educativas para o usuário.

## 📋 Visão Geral

O Detector de Golpes é uma aplicação completa (frontend + backend) projetada para ajudar usuários a identificar e se proteger contra fraudes financeiras. O sistema analisa mensagens recebidas e fornece uma avaliação de risco em tempo real, usando:

* Inteligência Artificial: Análise avançada de texto com Google Gemini
* Pesquisa Web: Enriquecimento da análise com informações atualizadas sobre golpes
* Verificação de Links: Identificação de URLs potencialmente maliciosas
* Conteúdo Educativo: Recomendações personalizadas e materiais informativos

## 🖼️ Screenshots

(Adicione aqui os screenshots da sua aplicação)

## 🏗️ Arquitetura

O projeto é composto por duas partes principais:

* **Backend (Python/FastAPI)**
    * API REST desenvolvida com FastAPI
    * Sistema de agentes especializados (análise de mensagens, verificação de links)
    * Integração com Google Gemini para análise de IA
    * Pesquisa na web para enriquecer a análise
* **Frontend (Vue.js)**
    * Interface de usuário intuitiva e responsiva
    * Comunicação assíncrona com o backend
    * Visualização amigável dos resultados da análise
    * Sistema de feedback para melhorar o algoritmo

## 🚀 Começando

Para começar a usar o Detector de Golpes, consulte os READMEs específicos:

* [Backend README](backend/README.md) - Instruções para configurar e executar o serviço backend
* [Frontend README](frontend/README.md) - Instruções para configurar e executar a interface de usuário

## 📊 Fluxo de Funcionamento

1.  O usuário cola uma mensagem suspeita no frontend
2.  A mensagem é enviada para o backend via API REST
3.  O backend processa a mensagem através de múltiplos agentes:
    * Analisador de mensagem (padrões linguísticos)
    * Verificador de links (URLs suspeitas)
    * Pesquisador web (correlação com golpes conhecidos)
    * Agente educacional (geração de conteúdo informativo)
4.  O resultado consolidado é enviado de volta ao frontend
5.  O frontend apresenta a análise, recomendações e materiais educativos
6.  O usuário pode fornecer feedback sobre a precisão da análise

## 🔒 Tipos de Golpes Detectados

* Golpes bancários (falsos funcionários, cartão bloqueado)
* Golpe do motoboy (coleta de cartão)
* Golpe do falso familiar (pedidos de dinheiro urgente)
* Falsos prêmios e promoções
* Phishing e sites maliciosos
* Entre outros

## 🙏 Contribuição

Contribuições são bem-vindas! Consulte os arquivos README específicos para orientações sobre como contribuir para cada parte do projeto.

## 📜 Licença

Este projeto está licenciado sob a Licença MIT.
