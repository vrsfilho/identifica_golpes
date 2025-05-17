<template>
  <div class="fraud-detector-container">
    <header>
      <h1>Detector de Golpes</h1>
      <p>Verifique se uma mensagem que você recebeu é suspeita de ser um golpe.</p>
    </header>

    <div class="input-section">
      <textarea
        v-model="userMessage"
        placeholder="Cole aqui a mensagem suspeita que você recebeu..."
        rows="6"
      ></textarea>

      <button
        :disabled="!userMessage || isAnalyzing"
        @click="analyzeMessage"
        class="analyze-button"
      >
        {{ isAnalyzing ? 'Analisando...' : 'Verificar Mensagem' }}
      </button>
    </div>

    <div
      v-if="analysisResult"
      :class="[
        'result-section',
        analysisResult.is_fraud ? 'fraud' : 'safe' // Aplica 'fraud' ou 'safe'
      ]"
    >
      <div class="result-header">
        <h2 v-if="analysisResult.is_fraud">
          <i class="material-icons">warning</i> Cuidado! Esta mensagem parece ser um golpe.
        </h2>
        <h2 v-else>
          <i class="material-icons">check_circle</i> Esta mensagem parece ser legítima.
        </h2>
        <div class="confidence">
          Confiança: {{ (analysisResult.confidence * 100).toFixed(0) }}%
        </div>
      </div>

      <div class="explanation">
        <h3>Análise:</h3>
        <p>{{ analysisResult.explanation }}</p>
      </div>

      <div class="recommendations">
        <h3>Recomendações:</h3>
        <ul>
          <li v-for="(rec, index) in analysisResult.recommendations" :key="index">{{ rec }}</li>
        </ul>
      </div>

      <div
        v-if="analysisResult.educational_text || (analysisResult.education_tips && analysisResult.education_tips.length > 0)"
        class="education"
      >
        <h3>Saiba mais sobre este tipo de golpe:</h3>
        <p v-if="analysisResult.educational_text">{{ analysisResult.educational_text }}</p>
        <ul v-if="analysisResult.education_tips && analysisResult.education_tips.length > 0">
          <li v-for="(tip, index) in analysisResult.education_tips" :key="'tip-' + index">{{ tip }}</li>
        </ul>
      </div>

      <div v-if="analysisResult.education_links && analysisResult.education_links.length > 0" class="education-links">
        <h3>Links Úteis:</h3>
        <ul>
          <li v-for="(link, index) in analysisResult.education_links" :key="'link-' + index">
            <a :href="link.url" rel="noopener noreferrer">{{ link.title }}</a>
          </li>
        </ul>
      </div>

      <div class="feedback">
        <p>Esta análise foi útil?</p>
        <button
          @click="reportFeedback(analysisResult.analysis_id, 'false_positive')"
          :disabled="feedbackSent"
          v-if="analysisResult.is_fraud"
        >
          Não é golpe
        </button>
        <button
          @click="reportFeedback(analysisResult.analysis_id, 'false_negative')"
          :disabled="feedbackSent"
          v-else
        >
          É golpe
        </button>
        <span v-if="feedbackSent" class="feedback-message">Obrigado pelo feedback!</span>
      </div>
    </div>

    <div v-if="errorMessage" class="error-message">
      <i class="material-icons">error</i> {{ errorMessage }}
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      userMessage: '',
      analysisResult: null,
      isAnalyzing: false,
      feedbackSent: false,
      errorMessage: null,
      apiUrl: 'http://localhost:8000'
    };
  },
  methods: {
    async analyzeMessage() {
      this.analysisResult = null;
      this.errorMessage = null;
      this.feedbackSent = false;

      if (!this.userMessage) {
        this.errorMessage = "Por favor, cole uma mensagem para analisar.";
        return;
      }

      this.isAnalyzing = true;

      try {
        const response = await axios.post(`${this.apiUrl}/analyze`, {
          message: this.userMessage,
          user_id: 'mobile-user-123',
          device_info: {
            platform: 'mobile',
            os: this.detectOperatingSystem()
          }
        });
        this.analysisResult = response.data;
        console.log("Resultado da análise:", this.analysisResult);
      } catch (error) {
        console.error('Erro ao analisar mensagem:', error);
        this.errorMessage = "Ocorreu um erro ao analisar sua mensagem. Por favor, tente novamente mais tarde.";
      } finally {
        this.isAnalyzing = false;
      }
    },

    async reportFeedback(analysisId, feedbackType) {
      if (this.feedbackSent) return;

      try {
        await axios.post(`${this.apiUrl}/feedback`, {
          analysis_id: analysisId,
          feedback_type: feedbackType
        });
        this.feedbackSent = true;
      } catch (error) {
        console.error('Erro ao enviar feedback:', error);
      }
    },

    detectOperatingSystem() {
      const userAgent = navigator.userAgent;
      if (/android/i.test(userAgent)) return 'Android';
      if (/iPad|iPhone|iPod/.test(userAgent)) return 'iOS';
      if (/windows phone/i.test(userAgent)) return 'Windows Phone';
      if (/mac/i.test(userAgent)) return 'MacOS';
      if (/windows/i.test(userAgent)) return 'Windows';
      if (/linux/i.test(userAgent)) return 'Linux';
      return 'Unknown';
    }
  }
};
</script>

<style scoped>
/* Estilos específicos para este componente */
.fraud-detector-container {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

header {
  text-align: center;
  margin-bottom: 20px;
}

header h1 {
  color: #333;
  font-size: 1.8em;
  margin-bottom: 5px;
}

header p {
  color: #666;
  font-size: 1em;
}

.input-section {
  margin-bottom: 20px;
}

textarea {
  width: 100%;
  padding: 12px;
  margin-bottom: 15px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
  font-size: 1em;
  resize: vertical;
}

.analyze-button {
  display: block;
  width: 100%;
  padding: 14px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.1em;
  transition: background-color 0.3s ease;
  text-align: center;
}

.analyze-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.analyze-button:hover:not(:disabled) {
  background-color: #0056b3;
}

.result-section {
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #ddd;
  margin-top: 20px;
}

/* Estilos para Fraude (Vermelho) */
.result-section.fraud {
  background-color: #f8d7da;
  border-color: #f5c6cb;
  color: #721c24;
}

/* Estilos para Seguro (Verde) */
.result-section.safe {
  background-color: #d4edda;
  border-color: #c3e6cb;
  color: #155724;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  font-weight: bold;
}

.result-header h2 {
  margin: 0;
  font-size: 1.3em;
  display: flex;
  align-items: center;
}

.result-header h2 i.material-icons {
  margin-right: 8px;
  font-size: 1.4em;
}

.confidence {
  font-size: 1em;
  white-space: nowrap;
}

.explanation,
.recommendations,
.education,
.education-links {
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.explanation:last-child,
.recommendations:last-child,
.education:last-child,
.education-links:last-child {
  border-bottom: none;
  padding-bottom: 0;
  margin-bottom: 0;
}

.explanation h3,
.recommendations h3,
.education h3,
.education-links h3 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 1.1em;
  color: #555;
}

.recommendations ul,
.education ul,
.education-links ul {
  padding-left: 20px;
  margin: 0;
}

.recommendations li,
.education li,
.education-links li {
  margin-bottom: 8px;
  line-height: 1.4;
}

.education-links a {
  color: #007bff;
  text-decoration: none;
}

.education-links a:hover {
  text-decoration: underline;
}

.feedback {
  margin-top: 20px;
  text-align: center;
  padding-top: 15px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.feedback p {
  margin-bottom: 10px;
  font-size: 1em;
  color: #555;
}

.feedback button {
  margin: 0 8px;
  padding: 10px 18px;
  border: 1px solid #007bff;
  border-radius: 4px;
  background-color: white;
  color: #007bff;
  cursor: pointer;
  font-size: 0.9em;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.feedback button:hover:not(:disabled) {
  background-color: #007bff;
  color: white;
}

.feedback button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.feedback-message {
  margin-left: 15px;
  font-size: 0.9em;
  color: #28a745;
  font-weight: bold;
}

.error-message {
  margin-top: 20px;
  padding: 15px;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
  border-radius: 4px;
  display: flex;
  align-items: center;
  font-size: 1em;
}

.error-message i.material-icons {
  margin-right: 10px;
  font-size: 1.4em;
}
</style>