# Detector de Golpes - Frontend

Interface de usuário intuitiva desenvolvida com Vue.js para interação com o sistema de detecção de golpes.

## 📋 Visão Geral

O frontend do Detector de Golpes oferece uma interface simples e amigável para que os usuários possam submeter mensagens suspeitas para análise. A aplicação exibe de forma clara o resultado da análise, recomendações e conteúdo educativo sobre golpes.

## ✨ Características

* Interface intuitiva: Design limpo e fácil de usar
* Feedback visual claro: Indicações visuais de risco (vermelho para golpe, verde para seguro)
* Análise detalhada: Exibição do nível de confiança e explicações
* Conteúdo educativo: Dicas personalizadas para o tipo específico de golpe
* Sistema de feedback: Permite aos usuários reportar falsos positivos/negativos
* Design responsivo: Funciona bem em dispositivos móveis e desktop

## 🚀 Instalação

### Pré-requisitos

* Node.js 16+ e npm (ou yarn)
* Backend configurado e funcionando (veja o README do Backend)

### Passos para instalação

1.  Clone o repositório (se ainda não o fez):

    ```bash
    git clone [https://github.com/seu-usuario/detector-golpes.git](https://github.com/seu-usuario/detector-golpes.git)
    cd detector-golpes/frontend
    ```

2.  Instale as dependências:

    ```bash
    npm install
    #   ou
    yarn install
    ```

3.  Configure a URL da API editando o arquivo `.env.local`:

    ```
    VITE_API_URL=http://localhost:8000
    ```

4.  Inicie o servidor de desenvolvimento:

    ```bash
    npm run dev
    #   ou
    yarn dev
    ```

    O aplicativo estará disponível em http://localhost:5173.

## 🔧 Construção para produção

Para construir o aplicativo para produção:

```bash
npm run build
#   ou
yarn build
```

Os arquivos serão gerados no diretório `dist/`.

## 🏗️ Estrutura de Componentes

O frontend é organizado com os seguintes componentes principais:

* `App.vue`: Componente raiz que contém o layout básico
* `components/FraudDetector.vue`: Componente principal para análise de mensagens

### Componente FraudDetector

Este componente é responsável por:

* Receber a entrada do usuário (mensagem suspeita)
* Enviar a mensagem para análise via API
* Exibir os resultados da análise
* Permitir feedback do usuário

## 📱 Fluxo do Usuário

1.  O usuário acessa a aplicação web
2.  Cola o texto da mensagem suspeita no campo de entrada
3.  Clica no botão "Verificar Mensagem"
4.  A aplicação exibe um indicador de carregamento enquanto processa
5.  O resultado da análise é exibido com:
    * Indicação clara se é golpe ou não
    * Nível de confiança da análise
    * Explicação detalhada
    * Recomendações específicas
    * Conteúdo educativo sobre o tipo de golpe
    * Links úteis para mais informações
6.  O usuário pode dar feedback sobre a precisão da análise

## 🎨 Personalização

### Temas e Cores

As cores principais usadas no aplicativo estão definidas nos arquivos CSS:

* Azul principal: `#007bff`
* Verde (seguro): `#28a745`
* Amarelo (aviso): `#ffc107`
* Vermelho (perigo): `#dc3545`

Para modificar o tema, edite os arquivos de estilo em cada componente Vue.

## 🔌 Integração com o Backend

A comunicação com o backend é feita utilizando axios. A configuração está no componente `FraudDetector.vue`:

```javascript
// URL base do seu backend FastAPI
apiUrl: 'http://localhost:8000'
```

Para modificar a URL da API em produção, ajuste o arquivo `.env.production`.

## 🛠️ Solução de Problemas

### Erro de CORS

**Problema:** Erros de CORS ao conectar com o backend

**Solução:**

* Verifique se o backend está configurado para permitir requisições do host do frontend
* No backend, atualize a lista de origins permitidas em `main.py`

### Erros de API

**Problema:** Mensagens de erro ao enviar requisições

**Solução:**

* Verifique se o backend está em execução
* Confirme se a URL da API está correta em `FraudDetector.vue`
* Verifique os logs do backend para erros específicos

## 📜 Licença

Este projeto está licenciado sob a Licença MIT.
