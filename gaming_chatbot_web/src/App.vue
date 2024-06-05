<script setup>
import HelloWorld from './components/HelloWorld.vue'
</script>
<template>
  <div class="container">
        <div class="card" style="border: none;">
          <div class="card-body" style="padding: 0; padding-top: 20px;">
            <div class="card-title">
              <div class="row">
                <div class="col-9 d-flex justify-content-center">
                  <h5>Gaming Chatbot</h5>
                </div>
              </div>     
            </div>
          </div>
        
          <div style="padding: 20px; max-height:1000px; height:69vh; overflow-y: auto;">
            <div v-for="(dialogue, index) in dialogue_history" :key="index">
              <div class="my-4" ref="'dialogue_' + index" :id="'dialogue_' + index">
                <div v-if="dialogue.role === 'assistant'" class="toast-header">
                  <strong class="me-auto">{{ agent_name }} (Bot)</strong>
                  <span class="badge text-bg-info">{{ dialogue.state }}</span>
                </div>
                <div v-if="dialogue.role === 'user'" class="toast-header">
                  <strong class="me-auto" v-if="dialogue.role === 'user'">User</strong>
                      <span v-if="dialogue.state !== null" class="badge text-bg-info">{{
                        dialogue.state
                      }}</span>
                </div>
                <div class="toast-body mt-2">
                  <span style="white-space: pre-line">{{ dialogue.content }}</span>
                </div>
              </div>
              <hr/>
            </div>
            <div class="my-4">
              <div class="toast-header placeholder-glow">
                <div class="alert alert-danger my-4" role="alert" v-if="response_error">
                  Server Error! Please refresh the page and try again later.
                </div>
                <form class="mt-3" @submit.prevent="sendChat" style="position: sticky; bottom: 20px;">
                  <v-row class="mt-2">
                    <v-col>
                      <v-textarea
                        v-model="user_input"
                        id="inputResponse"
                        placeholder="Send a message..."
                        rows="1"
                        max-rows="3"
                        counter
                        
                        hide-details
                        auto-grow
                        autofocus
                        maxlength="500"
                        append-inner-icon="mdi-arrow-up"
                        @keydown.stop.enter.exact.prevent="sendChat"
                        @keydown.enter.shift.exact.prevent="user_input += '\n'"
                        aria-label="Send"
                        @click:append-inner="sendChat"
                      ></v-textarea>
                    </v-col>
                  </v-row>
                </form>
              </div>
            </div>
          </div>
        </div>
  </div>
</template>

<style>
  .no-padding {
    padding-right: 0 !important;
    padding-left: 0 !important;
  }
</style>

<script >
import axios from 'axios'
export default {
  name: 'App',
  data() {
    return {
      dialogue_history: [],
      agent_name: 'Stragety Scraper',
      user_input: '',
      response_generate_loading: false,
      select_chatbot_loading: true,
      response_error: false,
    }
  }, 
  mounted() {
    this.dialogue_history = [
    ]
    this.startChat()
  },
  methods:{
    startChat(){
      axios
        .post(import.meta.env.VITE_API_BASE_URL + '/api/create', {
        })
        .then((response) => {
          this.dialogue_history.push({
            role: response.data['response']['role'],
            content: response.data['response']['content']
          })
          console.log(this.dialogue_history)
          this.select_chatbot_loading = false
        })
        .catch((error) => {
          console.log(error)
          this.select_chatbot_loading = false
        })
    },
    sendChat(e){
      if (this.response_generate_loading || e.isComposing || this.user_input.trim() == '') {
        return
      }
      const temp_user_input = this.user_input.trim()
      this.user_input = ''
      this.response_generate_loading = true
      this.dialogue_history.push({
        role: 'user',
        content: temp_user_input
      })
      axios
      .post(import.meta.env.VITE_API_BASE_URL + '/api/chat', {
        content: temp_user_input
      })
      .then((response) => {
        this.dialogue_history.push({
          role: response.data['response']['role'],
          content: response.data['response']['content'],
        })
        this.response_generate_loading = false
      })
      .catch((error) => {
        console.log(error)
        this.response_error = true
        this.response_generate_loading = false
      })
    }
  }
}
</script>
