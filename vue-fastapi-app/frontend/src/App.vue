<template>
  <div>
    <LinkForm @link-submitted="onLinkSubmitted" />
    <FileUploadForm @file-uploaded="onFileUploaded" />
    <div>
      <StreamingOutput :chunks="streamingChunks" />
      <button v-if="allStreamingChunksReceived" @click="downloadStreamingFile">Download Streaming File</button>

      <StreamingOutput :chunks="reversedStreamingChunks" />
      <button v-if="allReversedChunksReceived" @click="downloadReversedStreamingFile">Download Reversed Streaming File</button>
    </div>
  </div>
</template>

<script>
/* eslint-disable */
import LinkForm from './components/LinkForm.vue';
import FileUploadForm from './components/FileUploadForm.vue';
import StreamingOutput from './components/StreamingOutput.vue';
import axios from 'axios';

export default {
  components: {
    LinkForm,
    FileUploadForm,
    StreamingOutput,
  },
  data() {
    return {
      allStreamingChunksReceived: false,
      streamingChunks: [],
      allReversedChunksReceived: false,
      reversedStreamingChunks: [],
      streamingFileDownloadUrl: '',
      reversedStreamingFileDownloadUrl: ''
    };
  },
  methods: {
    async onLinkSubmitted(response) {
      await this.streamData(response);
    },
    async onFileUploaded(response) {
      await this.streamData(response);
    },
    async streamData(response) {
      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      const chunks = [];
      this.allStreamingChunksReceived = false;
      this.streamingChunks = [];
      this.allReversedChunksReceived = false;
      this.reversedStreamingChunks = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          this.allStreamingChunksReceived = true;
          if (this.allReversedChunksReceived) {
            await this.generateFilesFromText();
          }
          break;
        }

        const newChunk = decoder.decode(value, { stream: true });
        chunks.push(newChunk);

        // Start fetching reversed chunk asynchronously without waiting for it to finish
        this.fetchReversedChunk(newChunk);

        this.streamingChunks = [...chunks];
      }
    },

    async fetchReversedChunk(chunk) {
      const decoder = new TextDecoder();

      const reversedResponse = await fetch('http://localhost:8001/generate_text_chunks/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: chunk })
      });

      const reversedReader = reversedResponse.body.getReader();
      let reversedText = '';
      while (true) {
        const { done, value } = await reversedReader.read();
        if (done) break;
        reversedText += decoder.decode(value, { stream: true });
      }

      // Update reversed streaming chunks
      this.reversedStreamingChunks = [...this.reversedStreamingChunks, reversedText];
      if (this.reversedStreamingChunks.length === this.streamingChunks.length) {
        this.allReversedChunksReceived = true;
        if (this.allStreamingChunksReceived) {
          await this.generateFilesFromText();
        }
      }
    },

    async generateFilesFromText() {
      try {
        const streamingText = this.streamingChunks.join('');
        const reversedStreamingText = this.reversedStreamingChunks.join('');

        // Call backend to generate files from text
        const streamingFileResponse = await axios.post('http://localhost:8001/generate_file_from_text/', { text: streamingText });
        const reversedStreamingFileResponse = await axios.post('http://localhost:8001/generate_file_from_text/', { text: reversedStreamingText });

        this.streamingFileDownloadUrl = window.URL.createObjectURL(new Blob([streamingFileResponse.data]));
        this.reversedStreamingFileDownloadUrl = window.URL.createObjectURL(new Blob([reversedStreamingFileResponse.data]));
      } catch (error) {
        console.error('Error generating files from text:', error);
      }
    },

    downloadStreamingFile() {
      const link = document.createElement('a');
      link.href = this.streamingFileDownloadUrl;
      link.download = 'streaming_file.txt';
      document.body.appendChild(link);
      link.click();
    },

    downloadReversedStreamingFile() {
      const link = document.createElement('a');
      link.href = this.reversedStreamingFileDownloadUrl;
      link.download = 'reversed_streaming_file.txt';
      document.body.appendChild(link);
      link.click();
    }
  }
};
</script>
