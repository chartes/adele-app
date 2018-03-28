import Vue from 'vue';
import Vuex from 'vuex';

import user from './modules/user'
import document from './modules/document'

Vue.use(Vuex);
console.log('STORE');

export default new Vuex.Store({
    modules: {
      document,
      user
    }
});
