import Vue from 'vue';
import Vuex from 'vuex';

import user from './modules/user'
import document from './modules/document'
import transcription from './modules/transcription'
import translation from './modules/translation'
import noteTypes from './modules/noteTypes'
import notes from './modules/notes'

import axios from 'axios';

Vue.use(Vuex);

export default new Vuex.Store({
    modules: {
      document,
      noteTypes,
      notes,
      transcription,
      translation,
      user
    }
});
