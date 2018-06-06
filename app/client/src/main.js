import Vue from 'vue';
import App from './App.vue';

import store from './store'

new Vue({
  el: '#app',
  store,
  data: {
    documentId: undefined,
    authToken: undefined
  },
  beforeMount: function () {
    this.documentId = this.$el.dataset.documentId;
    this.authToken = this.$el.dataset.authToken;
    console.log("AUTH", this.$el.dataset)
  },
  render (h) {
    return h(App, { props: {
        doc_id: this.documentId,
        auth_token: this.authToken,
      }
    })
  }

});
