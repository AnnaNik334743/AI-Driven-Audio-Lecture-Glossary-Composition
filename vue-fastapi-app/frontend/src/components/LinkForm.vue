<template>
  <div class="input-container">
    <input v-model="link" type="text" placeholder="Enter YouTube URL" class="text-input">
    <button @click="processLink" class="submit-button">Загрузить ссылку</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      link: ''
    };
  },
  methods: {
    async processLink() {
      if (this.link.trim() !== '') {
        try {
          const response = await fetch('http://localhost:8001/api/asr/transcribe_file_chunks/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: this.link })  // так по-тупому, потому что валидация на стороне бэка
          });
          this.$emit('link-submitted', response);  // триггер события в App.vue
        } catch (error) {
          console.error('Error:', error);
        }
      }
    }
  }
};
</script>
