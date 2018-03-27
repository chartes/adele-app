<template>

  <div>

    <tabs>

      <tab name="Transcription" :selected="true">

        <h1 class="title">Transcription</h1>
        <div class="columns">
          <div class="column is-one-third">
            <h1>Transcription</h1>
            <div class="editor-controls">
              <button class="button is-small " :class="{'is-info':transcription.toolbar.bold}" @click="simpleFormat(transcription, 'bold')"><i class="fa fa-bold"></i></button>
              <button class="button is-small" :class="{'is-info':transcription.toolbar.italic}" @click="simpleFormat(transcription, 'italic')"><i class="fa fa-italic"></i></button>
              <button class="button is-small" :class="{'is-info':transcription.toolbar.smallcaps}" @click="simpleFormat(transcription, 'smallcaps')" style="font-variant: small-caps;font-weight: bold">Tt</button>
              <button class="button is-small" :class="{'is-info':transcription.toolbar.superscript}" @click="simpleFormat(transcription, 'superscript')"><i class="fa fa-superscript"></i></button>
              <button class="button is-small" :class="{'is-info':transcription.toolbar.underline}" @click="simpleFormat(transcription, 'underline')"><i class="fa fa-underline"></i></button>
              <br>
              <button class="button is-small" :class="{'is-info':transcription.toolbar.abbreviation}" @click="simpleFormat(transcription, 'expan')">(...)</button>
              <button class="button is-small" :class="{'is-info':transcription.toolbar.del}" @click="simpleFormat(transcription, 'del')"><i class="fa fa-strikethrough"></i></button>
              <button class="button is-small" :class="{'is-info':transcription.toolbar.link}" @click="linkFormat(transcription)"><i class="fa fa-link"></i></button>
              <button class="button is-small" :class="{'is-info':transcription.toolbar.blockquote}" @click="simpleFormat(transcription, 'blockquote')"><i class="fa fa-quote-left"></i>&nbsp;<i class="fa fa-quote-right"></i></button>
              <button class="button is-small" :class="{'is-info':transcription.toolbar.inlinequote}" @click="simpleFormat(transcription, 'inlinequote')"><i class="fa fa-quote-right"></i></button>
              <button class="button is-small" :class="{'is-info':transcription.toolbar.cite}" @click="linkFormat(transcription)"><i class="fa fa-book"></i></button>
              <button class="button is-small" :class="{'is-info':transcription.toolbar.person}" @click="linkFormat(transcription)"><i class="fa fa-user"></i></button>
              <button class="button is-small" :class="{'is-info':transcription.toolbar.location}" @click="linkFormat(transcription)"><i class="fa fa-map-marker"></i></button>
              <br>
              <button class="button is-small" :class="{'is-info':transcription.toolbar.division}" @click="simpleFormat(transcription, 'division')">DIV</button>
              <button class="button is-small" :class="{'is-info':transcription.toolbar.title}" @click="">H</button>
              <button class="button is-small" :class="{'is-info':transcription.toolbar.paragraph}" @click="">P</button>
              <button class="button is-small" :class="{'is-info':transcription.toolbar.list}" @click="simpleFormat(transcription, 'list')"><i class="fa fa-list"></i></button>
              <button class="button is-small" :class="{'is-info':transcription.toolbar.verse}" @click="">V</button>
              <button class="button is-small" :class="{'is-info':transcription.toolbar.linebreak}" @click="">lb</button>
              <button class="button is-small" :class="{'is-info':transcription.toolbar.columnbreak}" @click="">cb</button>
              <button class="button is-small" :class="{'is-info':transcription.toolbar.note}" @click=""><i class="fa fa-comment"></i></button>
            </div>
            <div id="transcription-container" class="quill-editor" ref="transcriptionEd" v-html="initialTranscription"></div>
            <hr>
            <h1>Delta dernière op.</h1>
            <pre>{{ transcription.lastOperations }}</pre>
          </div>
          <div class="column is-one-third">
            <h1>HTML</h1>
            <pre>{{ transcription.rendered }}</pre>
            <h1>Delta</h1>
            <pre>{{ transcription.delta }}</pre>
          </div>
          <div class="column is-one-third">
            <h1>Parties du discours</h1>
            <div v-html="speechparts.rendered"></div>
            <pre>{{ speechparts.delta }}</pre>
          </div>
        </div>

      </tab>

      <tab name="Traduction">

        <h1 class="title">Traduction</h1>

        <div class="columns">
          <div class="column is-one-third">
            <h1>Traduction</h1>
            <div class="editor-controls">
              <button class="button" @click="expanFormat(translation)">Expan</button>
              <button class="button" @click="persoFormat(translation)">Perso</button>
              <button class="button" @click="firstnameFormat(translation)">First name</button>
              <button class="button" @click="boldFormat(translation)"><i class="fa fa-bold"></i></button>
              <button class="button" @click="italicFormat(translation)"><i class="fa fa-italic"></i></button>
              <button class="button" @click="linkFormat(translation)"><i class="fa fa-link"></i></button>
            </div>
            <div id="translation-container" class="quill-editor" v-html="initialTranslation"></div>
          </div>
          <div class="column is-one-third">
          </div>
          <div class="column is-one-third">
            <pre>{{ translation.delta }}</pre>

          </div>
        </div>

      </tab>

      <tab name="Alignement">
        <h1 class="title">Alignement</h1>
        <div class="columns">
          <div class="column is-one-third">
            <h1>Transcription</h1>
            <div id="transcription-align-container" ref="transcriptionAlignEd" class="quill-editor"></div>
            <h1>Delta</h1>
          </div>
          <div class="column is-one-third">
            <h1>Traduction</h1>
            <div id="translation-align-container" ref="translationAlignEd" class="quill-editor"></div>
            <h1>Delta</h1>
          </div>
          <div class="column is-one-third">

          </div>
        </div>

      </tab>

      <tab name="Facsimilé">
        <h1 class="title">Facsimilé</h1>
        <div class="columns">
          <div class="column is-one-third">
            <h1>Transcription</h1>
            <div id="transcription-align-container" ref="transcriptionAlignEd" class="quill-editor"></div>
            <h1>Delta</h1>
          </div>
          <div class="column is-one-third">
            <h1>Traduction</h1>
            <div id="translation-align-container" ref="translationAlignEd" class="quill-editor"></div>
            <h1>Delta</h1>
          </div>
          <div class="column is-one-third">

          </div>
        </div>

      </tab>

      <tab name="Parties du discours">

        <h1 class="title">Parties du discours</h1>
        <div class="columns">
          <div class="column is-one-third">
            <h1>Transcription</h1>
            <div class="editor-controls">
              <button class="button" @click="launchSpeechpartEdit" :disabled="!speechparts.editable">+ Partie</button>
            </div>
            <div class="wrapper">
              <div id="speech-parts-container" class="quill-editor" ref="speechPartsEd" v-html="initialSpeechparts"></div>
              <speechpart-actions v-show="speechparts.current" :style="actionsPosition" :edit="launchSpeechpartEdit" :delete="deleteSpeechpart"></speechpart-actions>
            </div>
            <hr>
            <h1>Dernière op.</h1>
            <pre>{{ speechparts.lastOperations }}</pre>

          </div>
          <div class="column is-one-third">
            <speechpart-form
              v-if="speechparts.currentEdit"
              :speechpart="speechparts.current"
              :save="saveSpeechpart"
              :cancel="closeSpeechpartEdit"
            ></speechpart-form>
          </div>
          <div class="column is-one-third">

            <pre>{{ speechparts.delta }}</pre>
          </div>
        </div>

      </tab>

    </tabs>

  </div>

</template>

<script>

  import Quill from 'quill';
  import  '../modules/quill/Blots';

  import tabs from './ui/tabs.vue'
  import tab from './ui/tab.vue'
  import { filterDeltaForSpeechParts } from '../modules/quill/DeltaUtils'
  import SpeechpartForm from "./ui/speechpart-form";
  import SpeechpartActions from "./ui/speechpart-actions";

  export default {
    name: "editor",

    components: {
      SpeechpartActions,
      SpeechpartForm,
      tabs,
      tab
    },

    data () {
        return {

          initialTranscription: '<section class="div">Om<abbr>n</abbr>ib<abbr>us</abbr> presentes litteras inspecturis, . . officialis Belvacensis, salutem in Domino.<br>Noverint universi quod in nostra constituti presentia Ricardus dictus de Gres de Sancto Felice et Aya ejus uxor et Eufemia eorum filia recognoverunt se imperpetuum vendidisse pro communi eorum utilitate ac necessitate abbati et conventui Sancti Geremari Flaviacensis quamdam peciam terre sementis quam habebant ex caduco Asceline de Amuchi, matertere dicti Ricardi, circiter sex minas continentem, sitam ante mesum de Amuchi, dictorum abbatis et conventus, quam ab eisdem abbate et conventu tenebant ad campipartem,</section>',
          initialTranslation: '<p>A tous ceux qui verront les présentes lettres, . . l\'official de Beauvais, salut dans le Seigneur.</p> <p>Sachent tous que constitués en notre présence Richard dit de Grez, de Saint-Félix, Aye son épouse et Euphémie leur fille ont reconnu qu\'ils ont vendu à perpétuité pour leur commune utilité et leur commun besoin à l\'abbé et au convent de Saint-Germer de Fly une pièce de terre arable qu\'ils avaient de l\'héritage d\'Asceline d\'Amuchy, tante maternelle dudit Richard, d\'environ six éminées, sise devant le metz d\'Amuchy qui appartient auxdits abbé et convent, et qu\'ils tenaient à champart des mêmes abbé et convent,</p>',
          initialSpeechparts: '<p>Omnibus presentes litteras inspecturis, . . officialis Belvacensis, salutem in Domino.</p><p><speechpart id="1" type="adresse" note="super adresse">Noverint universi quod in nostra constituti presentia Ricardus dictus</speechpart> <speechpart id="2" type="autrepartie" note="una eutre partie assez notable en soi">de Gres de Sancto Felice et Aya ejus uxor et Eufemia eorum filia recognoverunt se imperpetuum vendidisse pro communi eorum utilitate ac necessitate abbati et conventui Sancti Geremari Flaviacensis</speechpart> quamdam peciam terre sementis quam <speechpart id="3" type="Que dire ? &quot;Rien, c\'est inutile&quot;" note="12">habebant ex caduco Asceline de Amuchi</speechpart>, matertere dicti Ricardi, circiter sex minas continentem, sitam ante mesum de Amuchi, dictorum abbatis et conventus, quam ab eisdem abbate et conventu tenebant ad campipartem,</p>',

          transcription: {
            editor: null,
            rendered: null,
            delta: null,
            lastOperations: null,
            toolbar: {
              bold: false,
              italic: false,
              smallcaps: false,
              superscript: false,
              underline: false,
              abbreviation: false,
              del: false,
              link: false,
              blockquote: false,
              inlinequote: false,
              cite: false,
              person: false,
              location: false,
              division: false,
            },
          },
          translation: {
            editor: null,
            rendered: null,
            delta: null,
            lastOperations: null,
            toolbar: {
              expan: false,
              perso: false,
              firstname: false,
              bold: false,
              italic: false,
              link: false,
            },
          },

          /*transcriptionAlignEditor: null,
          transcriptionAlign: null,
          translationAlignEditor: null,
          translationAlign: null,
          translationSync: null,*/

          speechparts: {
            editor: null,
            rendered: null,
            delta: null,
            lastOperations: null,
            current: null,
            currentEdit: false,
            editable: false,
            toolbar: {
              expan: false,
              perso: false,
              firstname: false,
              bold: false,
              italic: false,
              link: false,
            },
            actionsPosition: {
              top: 0, left: 0, right: 0, bottom: 0
            }
          },
          speechpartsCategories: [
            'Adresse universelle', 'Suscription', 'Salut', 'Notification universelle',
            'Corps de l\'acte', 'Clause de promesse', 'Clause de garantie', 'Corroboration probatoire',
            'Date de temps', 'Date de lieu'
          ],
        }
    },

    mounted () {
        console.log("mounted");

      this.transcription.editor = new Quill('#transcription-container');
      this.transcription.editor.on('selection-change', this.onTranscriptionSelection);
      this.transcription.editor.on('text-change', this.onTranscriptionTextChange);
      let transcriptionFilteredDelta = filterDeltaForSpeechParts(this.transcription.editor.getContents());


      this.translation.editor = new Quill('#translation-container');
      //let translationFilteredDelta = filterDeltaForSpeechParts(this.translation.editor.getContents());

      /*
      this.transcriptionAlignEditor = new Quill('#transcription-align-container');
      //this.transcriptionAlignEditor.enable(false);
      this.translationAlignEditor = new Quill('#translation-align-container');
      //this.translationAlignEditor.enable(false);
      this.$refs.transcriptionAlignEd.addEventListener('keydown', this.preventInsertionAndDeletion)
      this.$refs.translationAlignEd.addEventListener('keydown', this.preventInsertionAndDeletion)
      */

      this.speechparts.editor = new Quill('#speech-parts-container');
      this.speechparts.editor.on('selection-change', this.onSpeechPartsSelection);
      this.$refs.speechPartsEd.addEventListener('keydown', this.preventAllKeysButArrows)
      //this.speechparts.editor.setContents(transcriptionFilteredDelta);
      this.speechparts.editor.on('text-change', this.onSpeechPartsTextChange);

      this.updateContent();
    },

    methods: {

      onTranscriptionTextChange (delta, oldDelta, source) {
        console.log('onTranscriptionTextChange', delta, oldDelta, source)
        this.transcription.lastOperations = delta;
        let speechPartsDelta = this.speechparts.editor.getContents();
        let updatedDelta = speechPartsDelta.compose(filterDeltaForSpeechParts(delta));
        this.speechparts.editor.setContents(updatedDelta);
        this.updateContent();
      },
      onSpeechPartsTextChange (delta, oldDelta, source) {
        console.log('onSpeechPartsTextChange', delta, oldDelta, source)
        this.speechparts.lastOperations = delta;
        this.updateContent();
      },
      onTranscriptionSelection (range, oldRange, source) {
        if (range) {
          let formats = this.transcription.editor.getFormat(range.index, range.length);
          this.updateToolbarButtons(this.transcription.toolbar, formats)
        }
      },
      onSpeechPartsSelection (range, oldRange, source) {
        console.log('onSpeechPartsSelection')
        if (range && range.length > 0) {
          this.speechparts.editable = true;
          let text = this.speechparts.editor.getText(range.index, range.length);
          let format = this.speechparts.editor.getFormat(range.index, range.length);
          this.speechparts.current = null;
          if (format.speechpart) {
            this.speechparts.current = format.speechpart;
            console.log("speechparts.current", this.speechparts.current);
            let rangeBounds = this.speechparts.editor.getBounds(range);
            this.speechparts.actionsPosition.left = rangeBounds.left;
            this.speechparts.actionsPosition.right = rangeBounds.right;
            this.speechparts.actionsPosition.bottom = rangeBounds.bottom;
            console.log("%c bounds", 'color:#ff0000;', rangeBounds)
          } else {
            this.resetCurrentSpeechpart();
          }
        } else {
          this.speechparts.editable = false;
          this.resetCurrentSpeechpart();
        }
      },

      preventInsertionAndDeletion (e) {
        console.log("transcriptionAlignEd", e, e.keyCode);
        if (e.keyCode !== 13) {
          e.preventDefault()
        }
      },
      preventAllKeysButArrows (e) {
        console.log("transcriptionAlignEd", e, e.keyCode);
        if (!(e.key === 'ArrowUp' || e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === 'ArrowLeft'
          || e.key === 'Alt' || e.key === 'Meta' || e.key === 'Control' || e.key === 'Shift')) {
          e.preventDefault()
        }
      },

      updateToolbarButtons (whichToolbar, formats) {
        console.group("Selected formats", formats);
        for (let key in whichToolbar) {
          console.log(key, formats[key], !!formats[key])
          whichToolbar[key] = !!formats[key];
        }
        console.groupEnd();
      },

      updateContent () {
        console.log("updateContent", this.transcription.editor, this.translation.editor,  this.speechparts.editor)
        this.transcription.delta = this.transcription.editor.getContents().ops;
        this.transcription.rendered = this.$refs.transcriptionEd.childNodes[0].innerHTML;
        this.translation.delta = this.translation.editor.getContents().ops;
        this.speechparts.delta = this.speechparts.editor.getContents().ops;
        console.log(this.$refs.speechPartsEd)
        console.log(this.$refs.speechPartsEd.childNodes)
        console.log(this.$refs.speechPartsEd.childNodes[0])
        console.log(this.$refs.speechPartsEd.childNodes[0].innerHTML)
        this.speechparts.rendered = this.$refs.speechPartsEd.childNodes[0].innerHTML;
      },

      extendSelectionToFitFormat () {

      },

      // Edit speech parts

      launchSpeechpartEdit () {
        console.log("launchSpeechpartEdit");
        this.speechparts.currentEdit = true;
      },
      closeSpeechpartEdit () {
        console.log("closeSpeechpartEdit");
        this.speechparts.currentEdit = false;
      },
      saveSpeechpart (updatedSpeechpart) {
        console.log("saveSpeechpart", updatedSpeechpart);
        // TODO SAVE
        this.speechparts.editor.format('speechpart', updatedSpeechpart);
        this.closeSpeechpartEdit();
      },
      deleteSpeechpart () {
        console.log("deleteSpeechpart");
      },
      resetCurrentSpeechpart () {
        this.speechparts.current = null;
        this.speechparts.actionsPosition.left = 0;
        this.speechparts.actionsPosition.right = 0;
        this.speechparts.actionsPosition.bottom = 0;
      },
      speechpartFormat () {
        let type = prompt('Choisissez le type de partie');
        let note = prompt('Saisissez une note additionnelle');
        this.speechparts.editor.format('speechpart', {type, note});
        this.updateContent();
      },

      // Formats

      expanFormat(whichEditor) {
        whichEditor.editor.format('expan', true);
        this.updateContent();
      },
      persoFormat(whichEditor) {
        whichEditor.editor.format('perso', true);
        this.updateContent();
      },
      firstnameFormat (whichEditor) {
        let url = prompt('Entrez une URL');
        let comment = prompt('Entrez un commentaire');
        whichEditor.editor.format('firstname', {url: url, comment:comment});
        this.updateContent();
      },
      linkFormat (whichEditor) {
        let value = prompt('Enter link URL');
        whichEditor.editor.format('link', value);
        this.updateContent();
      },
      simpleFormat(whichEditor, formatName) {
        let ed = whichEditor.editor;
        let selection = ed.getSelection();
        let format = ed.getFormat(selection.index, selection.length);
        let value = !format[formatName];
        ed.format(formatName, value);
        let formats = ed.getFormat(selection.index, selection.length);
        //this.updateContent();
        this.updateToolbarButtons(whichEditor.toolbar, formats)
      },

    },
    computed: {
      actionsPosition () {
        return 'top:' + (this.speechparts.actionsPosition.bottom + 5)+'px;left:'+ ((this.speechparts.actionsPosition.left+this.speechparts.actionsPosition.right)/2)+'px';
      }
    }

  }
</script>

<style scoped>

</style>
