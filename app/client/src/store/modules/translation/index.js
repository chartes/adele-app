import axios from 'axios';
import Quill from '../../../modules/quill/AdeleQuill';
import TEItoQuill, {insertNotes, computeNotesPointers} from '../../../modules/quill/MarkupUtils'

const state = {

  translation: undefined,
  translationWithNotes: undefined,
  translationSaved: false,
  translationHtml: null,
  shadowQuillElement: document.createElement('div',{ class: 'phantom-quill-translation'}),
  shadowQuill: null

};

const mutations = {

  TRANSLATION_INIT(state, payload) {
    if (!state.shadowQuill) {
      state.shadowQuillElement.innerHTML = payload;
      state.shadowQuill = new Quill(state.shadowQuillElement);
      state.translationHtml = payload;
    }
  },

  UPDATE_TRANSLATION (state, payload) {
    console.log("UPDATE_TRANSLATION")
    state.translation = payload.raw;
    state.translationWithNotes = payload.formatted;
    state.translationSaved = true;
  },
  TRANSLATION_CHANGED (state) {
    // translation changed and needs to be saved
    console.log("TRANSLATION_CHANGED")
    state.translationSaved = false;
  },
  TRANSLATION_ADD_OPERATION (state, payload) {
    state.shadowQuill.updateContents(payload);
    console.log("TRANSLATION_ADD_OPERATION", payload)
    state.translationHtml = state.shadowQuillElement.children[0].innerHTML;
  },
  TRANSLATION_SAVED (state) {
    // translation changed and needs to be saved
    console.log("TRANSLATION_CHANGED")
    state.translationSaved = false;
  }

};

const actions = {

  fetchTranslation ({ commit, getters, rootState }) {
    const doc_id = getters.document.id;
    const user_id = getters.currentUser.id;

    console.log('STORE ACTION fetchTranslation')

    axios.get(`/api/1.0/documents/${doc_id}/translations/from-user/${rootState.user.currentUser.id}`).then( response => {


      let translation = {content : " ", notes: []};

      if (response.data.data && response.data.data.length !== 0) {
        translation = response.data.data;
      }

      console.log("FETCHED TRANSLATION", translation);

      const content = translation.content;
      const notes = translation.notes;
      const formatted = insertNotes(content, notes);

      //console.log('formatted', formatted)

      commit('TRANSLATION_INIT', content)
      commit('UPDATE_TRANSLATION', { raw: translation, formatted: formatted });
    });

  },
  saveTranslation ({ commit, getters, rootState }, translationWithNotes) {

    console.log('STORE ACTION saveTranslation', translationWithNotes);


    // Save translation content without notes

    // count notes pointers
    const notes = computeNotesPointers(translationWithNotes);
    notes.forEach((note) => {
      let found = rootState.notes.notes.find((element) => {
        return element.id === note.note_id;
      });
      note.content = found.content;
    });
    console.log(notes);

    // remove notes


  },
  translationChanged ({ commit }, deltas) {
    commit('TRANSLATION_ADD_OPERATION', deltas)
    commit('TRANSLATION_SAVED', false)
  }

};

const getters = {
  translation: state => state.translation,
  translationWithNotes: state => state.translationWithNotes,
  translationContent: state => !!state.translation ? state.translation.content : null,
  translationIsSaved: state => state.translationSaved,
  translationHTML: state => state.translationHtml,
  //translationWithNotes: state =>
};

const translationModule = {
  state,
  mutations,
  actions,
  getters
}

export default translationModule;
