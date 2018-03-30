import Vue from 'vue';
import Vuex from 'vuex';

import user from './modules/user'
import document from './modules/document'
import transcription from './modules/transcription'

Vue.use(Vuex);

export default new Vuex.Store({
    modules: {
      document,
      transcription,
      user
    }
});
