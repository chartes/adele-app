<template>
    <form>
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
                <field-select :options="centuries" :selected="form.copy_cent" label="Siècle de la copie" :onChange="onChangeCentury"/>

                <hr>

                <field-select :options="institutionsSelect" :selected="institutionId" label="Institution de conservation" :onChange="onChangeInstitution"/>
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

                <field-multiselect :label="'Pays :'" :optionsList="countries" :selectedItems="form.countries" :onChange="onChangeCountries"/>
                <field-multiselect :label="'District(s) :'" :optionsList="districts" :selectedItems="form.districts" :onChange="onChangeDistricts"/>
                <field-multiselect :label="'Type(s) d\'acte(s) :'" :optionsList="actTypes" :selectedItems="form.acte_types" :onChange="onChangeActTypes"/>
                <field-multiselect :label="'Tradition(s) :'" :optionsList="traditions" :selectedItems="form.traditions" :onChange="onChangeTraditions"/>
                <field-multiselect :label="'Langage(s) :'" :optionIdField="'code'" :optionsList="languages" :selectedItems="form.languages" :onChange="onChangeLanguages"/>
                <field-multiselect :label="'Éditeur(s) :'" :optionLabelField="'name'" :optionsList="editors" :selectedItems="form.editors" :onChange="onChangeEditors"/>

            </div>


        </div>


        <div class="columns">
            <div class="column">
                <save-button :status="status" :text="'Enregistrer les modifications'" :action="submit"/>
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
  import SaveButton from "../ui/SaveButton";

  export default {
    components: {
      SaveButton,
      FieldMultiselect,
      EditorButton,
      FieldSelect},
    name: "notice-edition",

    mixins: [EditorMixins],

    data () {
      return {
        status: '',
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

      this.$refs.editor.innerHTML = this.document.argument;
      this.editor = getNewQuill(this.$refs.editor);
      this.editor.on('selection-change', this.onSelection);
      this.editor.on('selection-change', this.onFocus);
      this.editor.on('text-change', this.onTextChange);
      this.textLength = this.editor.getLength();

      this.form = Object.assign({}, this.document);

      console.log('this.$store.getters[\'institutions/getInstitutionById\']', this.$store.getters['institutions/getInstitutionById'])
    },
    methods: {

      submit () {
        let data = Object.assign({}, this.form);
        data.acte_types = this.form.acte_types.map(item => item.id);
        data.country_id = this.form.countries.map(item => item.id);
        data.district_id = this.form.districts.map(item => item.id);
        data.language_code = this.form.languages.map(item => item.code);
        data.tradition_id = this.form.traditions.map(item => item.id);
        data.institution_id = data.institution.id;
        console.log('submit', data);
        this.status = 'saving';

        this.$store.dispatch('document/save', data).then(response => {
          this.status = 'success';
        }).catch(e => {
          this.status = 'error';
        })

      },

      onSelectChange(typeId) {
        this.form.type_id = typeId;
      },
      onTextChange() {
        this.textLength = this.editor.getLength();
        this.form.argument = this.$refs.editor.childNodes[0].innerHTML;
      },
      onSelection(range) {
        if (range) {
          let formats = this.editor.getFormat(range.index, range.length);
          this.updateButtons(formats);
        }
      },

      onChangeCountries (countries) {
        console.log('onChangeCountries', countries);
        this.form.countries = countries;
      },
      onChangeDistricts (districts) {
        console.log('onChangeDistricts', districts);
        this.form.districts = districts;
      },
      onChangeActTypes (actTypes) {
        console.log('onChangeActTypes', actTypes);
        this.form.acte_types = actTypes;
      },
      onChangeTraditions (traditions) {
        console.log('onChangeTraditions', traditions);
        this.form.traditions = traditions;
      },
      onChangeLanguages (languages) {
        console.log('onChangeLanguages', languages);
        this.form.languages = languages;
      },
      onChangeEditors (editors) {
        console.log('onChangeEditors', editors);
        this.form.editors = editors;
      },
      onChangeCentury (century) {
        console.log('onChangeCentury', century);
        this.form.copy_cent = century;
      },
      onChangeInstitution (institutionId) {
        this.form.institution = this.institutionsSelect.find(i =>  i.id === institutionId);
      },
    },

    computed: {
      institutionId () {
        console.log('institutionId',  this.form.institution)
        return this.form.institution ? this.form.institution.id : null;
      },
      ...mapGetters('institutions', ['institutionsSelect']),
      ...mapState('actTypes', ['actTypes']),
      ...mapState('countries', ['countries']),
      ...mapState('districts', ['districts']),
      ...mapState('document', ['document']),
      ...mapState('editors', ['editors']),
      ...mapState('languages', ['languages']),
      ...mapState('traditions', ['traditions']),
    }
  }
</script>

<style scoped>

</style>