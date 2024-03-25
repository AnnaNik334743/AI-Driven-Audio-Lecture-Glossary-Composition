<template>
  <div class="input-container">
    <input type="file" ref="fileInput" accept=".mp3,.mp4,.wav" class="file-input">
    <button @click="uploadFile" class="submit-button">Загрузить файл</button>
  </div>
</template>

<script>
export default {
  methods: {
    async uploadFile() {
      const file = this.$refs.fileInput.files[0];
      if (!file) return;

      try {
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetch('http://localhost:8001/upload_file/', {
          method: 'POST',
          body: formData
        });

        this.$emit('file-uploaded', response);  // триггер события в App.vue
      } catch (error) {
        console.error('Error:', error);
      }
    }
  }
};
</script>
