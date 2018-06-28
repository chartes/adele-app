<template>
    <form action="">
        <div class="columns">


            <div class="column is-half">


                <div class="field">
                    <label class="label">Titre</label>
                    <div class="field-body">
                        <div class="field">
                            <div class="control">
                                <input class="input" v-model="form.title" type="text" placeholder="Titre">
                            </div>
                        </div>
                    </div>
                </div>
                <div class="field">
                    <label class="label">Sous-titre</label>
                    <div class="field-body">
                        <div class="field">
                            <div class="control">
                                <textarea class="textarea" v-model="form.subtitle" type="text" placeholder="Sous-titre"></textarea>
                            </div>
                        </div>
                    </div>
                </div>
                <hr>
                <div class="field">
                    <label class="label">Année de création</label>
                    <div class="field-body">
                        <div class="field">
                            <div class="control">
                                <input class="input" v-model="form.creation" type="number" placeholder="Année de création">
                            </div>
                        </div>
                    </div>
                </div>
                <div class="field">
                    <label class="label">Année de création (formatée)</label>
                    <div class="field-body">
                        <div class="field">
                            <div class="control">
                                <input class="input" v-model="form.creation_lab" type="text" placeholder="[1200-1210 ca.]">
                            </div>
                        </div>
                    </div>
                </div>
                <div class="field">
                    <label class="label">Année de la copie (formatée)</label>
                    <div class="field-body">
                        <div class="field">
                            <div class="control">
                                <input class="input" v-model="form.copy_year" type="text" placeholder="[1200-1210 ca.]">
                            </div>
                        </div>
                    </div>
                </div>
                <field-select :options="centuries" label="Siècle de la copie" :onChange="()=>{}"/>

                <hr>

                <field-select :options="institutionsSelect" :selected="institutionId" label="Institution de conservation" :onChange="()=>{}"/>
                <div class="field">
                    <label class="label">Pressmark</label>
                    <div class="field-body">
                        <div class="field">
                            <div class="control">
                                <input class="input" v-model="form.pressmark" type="text" placeholder="Cote">
                            </div>
                        </div>
                    </div>
                </div>
                <div class="field">
                    <p class="control">
                        <label class="label">Argument</label>
                    </p>
                    <div class="editor-area">
                        <div class="editor-controls" ref="controls">
                            <editor-button :selected="buttons.bold" :active="editorHasFocus" :callback="simpleFormat" :format="'bold'"/>
                            <editor-button :selected="buttons.italic" :active="editorHasFocus" :callback="simpleFormat" :format="'italic'"/>
                            <editor-button :selected="buttons.superscript" :active="editorHasFocus" :callback="simpleFormat" :format="'superscript'"/>
                            <editor-button :selected="buttons.smallcaps" :active="editorHasFocus" :callback="simpleFormat" :format="'smallcaps'"/>
                            <editor-button :selected="buttons.underline" :active="editorHasFocus" :callback="simpleFormat" :format="'underline'"/>
                            <editor-button :selected="buttons.del" :active="editorHasFocus" :callback="simpleFormat" :format="'del'"/>
                        </div>
                        <div class="quill-editor" ref="editor" spellcheck="false"></div>
                    </div>
                </div>


            </div>

            <div class="column is-half">

                <field-multiselect :label="'Pays :'" :optionsList="countries" :selectedItems="form.countries"/>
                <field-multiselect :label="'District(s) :'" :optionsList="districts" :selectedItems="form.districts"/>
                <field-multiselect :label="'Type(s) d\'acte(s) :'" :optionsList="actTypes" :selectedItems="form.acte_types"/>
                <field-multiselect :label="'Tradition(s) :'" :optionsList="traditions" :selectedItems="form.traditions"/>
                <field-multiselect :label="'Langage(s) :'" :optionIdField="'code'" :optionsList="languages" :selectedItems="form.languages"/>
                <field-multiselect :label="'Éditeur(s) :'" :optionLabelField="'name'" :optionsList="editors" :selectedItems="form.editors"/>

            </div>


        </div>


        <div class="columns">
            <div class="column">
                <button class="button is-primary" type="submit">Enregistrer les modifications</button>
            </div>
        </div>

    </form>
</template>

<script>

  import { mapState, mapGetters } from 'vuex';
  import { getNewQuill } from '../../modules/quill/AdeleQuill';
  import FieldSelect from '../forms/FieldSelect';
  import EditorMixins from '../../mixins/EditorMixins';
  import EditorButton from "../editors/EditorButton";
  import FieldMultiselect from "../forms/FieldMultiselect";

  export default {
    components: {
      FieldMultiselect,
      EditorButton,
      FieldSelect},
    name: "notice-edition",

    mixins: [EditorMixins],

    data () {
      return {
        form: {
        },
        centuries: [
          {id: null, label: 'Non défini'},
          {id: 10, label: 'X<sup>e</sup> s.'},
          {id: 11, label: 'XI<sup>e</sup> s.'},
          {id: 12, label: 'XII<sup>e</sup> s.'},
          {id: 13, label: 'XIII<sup>e</sup> s.'},
          {id: 14, label: 'XIV<sup>e</sup> s.'},
          {id: 15, label: 'XV<sup>e</sup> s.'},
          {id: 16, label: 'XVI<sup>e</sup> s.'},
          {id: 17, label: 'XVII<sup>e</sup> s.'},
          {id: 18, label: 'XVIII<sup>e</sup> s.'},
        ],
        editor: null,
        buttons: {
          bold: false,
          italic: false,
          superscript: false,
          smallcaps: false,
          underline: false,
          del: false,
        },
      }
    },
    mounted () {

      this.$store.dispatch('institutions/fetch');
      this.$store.dispatch('actTypes/fetch');
      this.$store.dispatch('countries/fetch');
      this.$store.dispatch('districts/fetch');
      this.$store.dispatch('editors/fetch');
      this.$store.dispatch('languages/fetch');
      this.$store.dispatch('traditions/fetch');

      this.$refs.editor.innerHTML = '';
      this.editor = getNewQuill(this.$refs.editor);
      this.editor.on('selection-change', this.onSelection);
      this.editor.on('selection-change', this.onFocus);
      this.editor.on('text-change', this.onTextChange);
      this.textLength = this.editor.getLength();

      this.form = Object.assign({}, this.document)
      console.log('data', this.form)
    },
    methods: {

      onSelectChange(typeId) {
        this.form.type_id = typeId;
      },
      onTextChange() {
        this.textLength = this.editor.getLength();
        this.form.content = this.$refs.editor.childNodes[0].innerHTML;
      },
      onSelection(range) {
        if (range) {
          let formats = this.editor.getFormat(range.index, range.length);
          this.updateButtons(formats);
        }
      },
    },

    computed: {
      institutionId () {
        return this.form.institution ? this.form.institution.id : null;
      },
      ...mapGetters('institutions', ['institutionsSelect']),
      ...mapState('actTypes', ['actTypes']),
      ...mapState('countries', ['countries']),
      ...mapState('districts', ['districts']),
      ...mapState('editors', ['editors']),
      ...mapState('languages', ['languages']),
      ...mapState('document', ['document']),
      ...mapState('traditions', ['traditions']),
    }
  }
</script>

<style scoped>

</style>