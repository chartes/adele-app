import Vue from 'vue'
import App from './App.vue'

require('./assets/styles/styles.scss');

new Vue({
  el: '#app',
  render: h => h(App)
})
