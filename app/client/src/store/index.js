import Vue from 'vue';
import Vuex from 'vuex';

import user from './modules/user'
import document from './modules/document'
import actTypes from './modules/actTypes'
import commentaries from './modules/commentaries'
import countries from './modules/countries'
import districts from './modules/districts'
import facsimile from './modules/facsimile'
import editors from './modules/editors'
import institutions from './modules/institutions'
import languages from './modules/languages'
import traditions from './modules/traditions'
import transcription from './modules/transcription'
import translation from './modules/translation'
import noteTypes from './modules/noteTypes'
import speechparts from './modules/speechparts'
import speechpartTypes from './modules/speechpartTypes'
import notes from './modules/notes'

Vue.use(Vuex);

export default new Vuex.Store({
    modules: {
      actTypes,
      commentaries,
      countries,
      districts,
      document,
      editors,
      facsimile,
      institutions,
      languages,
      noteTypes,
      notes,
      speechparts,
      speechpartTypes,
      traditions,
      transcription,
      translation,
      user
    }
});
