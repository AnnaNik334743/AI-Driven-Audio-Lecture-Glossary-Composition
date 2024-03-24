<template>
  <div>
    <input type="file" ref="fileInput" accept=".mp3,.mp4,.wav">
    <v-btn @click="uploadFile">Upload File</v-btn>
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

        this.$emit('file-uploaded', response);
      } catch (error) {
        console.error('Error:', error);
      }
    }
  }
};
</script>
