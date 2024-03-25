<template>
  <div class="form-container">
    <h2>Mock-up версия приложения</h2>

    <div class="form-item">
      <LinkForm @link-submitted="onLinkSubmitted" />
    </div>
    <div class="form-item">
      <FileUploadForm @file-uploaded="onFileUploaded" />
    </div>

    <div class="streaming-container">
      <div class="streaming-output">
        <h3>Транскрибация аудио</h3>
        <StreamingOutput :chunks="streamingChunks" />
        <button v-if="allStreamingChunksReceived" @click="downloadStreamingFile">Скачать транскрипт</button>
      </div>

      <div class="streaming-output">
        <h3>Генерация глоссария (списка терминов)</h3>
        <StreamingOutput :chunks="LLMStreamingChunks" />
        <button v-if="allLLMChunksReceived" @click="downloadLLMStreamingFile">Скачать глоссарий</button>
      </div>
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
      allStreamingChunksReceived: false,  // собираем текст на стороне фронта, по окончании отдадим бэку на модерацию
      streamingChunks: [],  // то, что отображается для пользователя

      allLLMChunksReceived: false,  // собираем текст на стороне фронта, по окончании отдадим бэку на модерацию
      LLMStreamingChunks: [],  // то, что отображается для пользователя

      streamingFileDownloadUrl: '',  // откуда потом скачивать итоговый файл для транскрипта
      LLMStreamingFileDownloadUrl: ''  // откуда потом скачивать итоговый файл для LLM
    };
  },
  methods: {
    async onLinkSubmitted(response) {
      await this.streamData(response);  // как только пользователь загрузил ссылку
    },

    async onFileUploaded(response) {
      await this.streamData(response);  // или файл
    },

    async streamData(response) {
      const reader = response.body.getReader();  // запускаем обработчик данных с бэка (на бэке Streaming text Response)
      const decoder = new TextDecoder();

      // своего рода делаем clear предыдущего содержимого, если оно было
      this.allStreamingChunksReceived = false;
      this.streamingChunks = [];
      this.allLLMChunksReceived = false;
      this.LLMStreamingChunks = [];

      while (true) {  // пока с бэка что-то идет - читаем это
        const { done, value } = await reader.read();
        if (done) {  // всё собрали?
          await this.generateFilesFromText();  // как только собрали, генерируем из собранного файл
          this.allStreamingChunksReceived = true;  // индикатор того, что файл можно скачивать
          break;  // и прекращаем выполнение
        }

        const newChunk = decoder.decode(value, { stream: true });  // забираем чанк с бэка
        this.streamingChunks.push(newChunk);  // обновляем содержимое общего массива чанков

        // как только новый кусочек пришел, кидаем его на обработку LLM. дальнейшая судьба кусочка в этой функции нас
        // не интересует (то есть мы не ждем, пока оно выполнится)
        this.fetchLLMChunk(newChunk);
      }
    },

    async fetchLLMChunk(chunk) {

      const LLMResponse = await fetch('http://localhost:8001/generate_text_chunks/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: chunk })
      });  // кидаем запрос на бэк

      const LLMReader = LLMResponse.body.getReader();  // как и в предыдущей функции, читаем Streaming Response
      const decoder = new TextDecoder();

      let LLMText = '';
      while (true) {
        const { done, value } = await LLMReader.read();
        if (done) break;
        LLMText += decoder.decode(value, { stream: true });

        console.log(LLMText)  // вот тут можно увидеть, как аккумулируется текст
      }

      // обновляем только после того, как нам вернулись все чанки. причина - важно сохранить последовательность
      // расчет на то, что генерация однородна по скорости, а значит что раньше начало выполняться, то раньше и закончит
      // P.S. на бэке есть пост-сортировка по времени, поэтому даже если что-то пойдет не так, в конце всё исправится
      this.LLMStreamingChunks = [...this.LLMStreamingChunks, LLMText];

      // как только обработали все чанки, пришедшие от транскрибатора за всё время, формируем файл и отдаем его пользователю
      if (this.LLMStreamingChunks.length === this.streamingChunks.length) {
        if (this.allStreamingChunksReceived) {
          await this.generateLLMFilesFromText();
          this.allLLMChunksReceived = true;  // индикатор того, что файл можно скачивать
        }
      }
    },

    // следующие две функции выглядят похоже и отвечают за превращение составленного по чанкам текста в файл
    // в дальнейшем они будут обращаться к разным эндпоинтам
    async generateFilesFromText() {
      try {
        const streamingText = this.streamingChunks.join('');
        const streamingFileResponse = await axios.post('http://localhost:8001/generate_file_from_text/', { text: streamingText });
        this.streamingFileDownloadUrl = window.URL.createObjectURL(new Blob([streamingFileResponse.data]));
        } catch (error) {
        console.error('Error generating files from text:', error);
      }
    },

    async generateLLMFilesFromText() {
      try {
        const LLMStreamingText = this.LLMStreamingChunks.join('');
        const LLMStreamingFileResponse = await axios.post('http://localhost:8001/generate_file_from_text/', { text: LLMStreamingText });
        this.LLMStreamingFileDownloadUrl = window.URL.createObjectURL(new Blob([LLMStreamingFileResponse.data]));
      } catch (error) {
        console.error('Error generating files from text:', error);
      }
    },

    // следующие две функции выглядят похоже и отвечают за предоставление пользователю возможности скачать файл
    downloadStreamingFile() {
      const link = document.createElement('a');
      link.href = this.streamingFileDownloadUrl;
      link.download = 'streaming_file.txt';
      document.body.appendChild(link);
      link.click();
    },

    downloadLLMStreamingFile() {
      const link = document.createElement('a');
      link.href = this.LLMStreamingFileDownloadUrl;
      link.download = 'LLM_streaming_file.txt';
      document.body.appendChild(link);
      link.click();
    }
  }
};
</script>

<style>
  .form-container {
    padding: 20px;
  }

  .form-item {
    margin-bottom: 20px;
  }

  .streaming-container {
    display: flex;
  }

  .streaming-output {
    margin-right: 20px;
    margin-bottom: 20px;
  }

  .input-container {
    margin-bottom: 20px;
  }

  .text-input {
    margin-right: 72px;
  }

  .submit-button {
  }
</style>