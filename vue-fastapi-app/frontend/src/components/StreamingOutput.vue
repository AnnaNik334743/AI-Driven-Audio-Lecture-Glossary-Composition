<template>
  <div>
    <textarea v-model="output" rows="10" cols="50" readonly></textarea>
  </div>
</template>

<script>
export default {
  props: {
    chunks: { type: Array, default: () => [] }
  },
  computed: {
    output() {
      return this.chunks.join('');
    }
  }
};
</script>
