<template>
  <div class="app-container">
    <header>
      <h1>Detector de Golpes</h1>
      <p>Verifique se uma mensagem pode ser uma tentativa de golpe</p>
    </header>
    
    <main>
      <FraudDetector />
    </main>
    
    <footer>
      <p>&copy; 2023 Detector de Golpes - Proteja-se contra fraudes online</p>
    </footer>
  </div>
</template>

<script>
import FraudDetector from './components/FraudDetector.vue'

export default {
  name: 'App',
  components: {
    FraudDetector
  }
}
</script>

<style>
.app-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

header {
  text-align: center;
  margin-bottom: 30px;
}

header h1 {
  color: #2c3e50;
  margin-bottom: 10px;
}

footer {
  margin-top: 40px;
  text-align: center;
  color: #666;
  font-size: 0.9em;
}
</style>