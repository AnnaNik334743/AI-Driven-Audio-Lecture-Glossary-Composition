<template>
  <div>
    <input v-model="link" type="text" placeholder="Enter URL">
    <button @click="processLink">Process Link</button>
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
          const response = await fetch('http://localhost:8001/process_link/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: this.link })  // text is because you need to validate strings in fastapi...
          });
          this.$emit('link-submitted', response);
        } catch (error) {
          console.error('Error:', error);
        }
      } else {
        // handle empty input case
      }
    }
  }
};
</script>
