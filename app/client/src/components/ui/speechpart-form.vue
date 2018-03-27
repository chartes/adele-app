<template>

  <div class="modal is-active">
    <div class="modal-background" @click="cancelAction"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">Editer {{form.type}}</p>
        <button class="delete" aria-label="close" @click="cancelAction"></button>
      </header>
      <section class="modal-card-body">
        <div class="speechpart-form">
          <form @submit.prevent="">
            <div class="field">
              <label class="label">ID</label>
              <div class="control">
                <input class="input" type="text" placeholder="ID" name="id" v-model="form.id">
              </div>
            </div>
            <div class="field">
              <label class="label">Type</label>
              <div class="control">
                <input class="input" type="text" placeholder="Type" name="type" v-model="form.type">
              </div>
            </div>
            <div class="field">
              <label class="label">Note</label>
              <div class="control">
                <input class="input" type="text" placeholder="Note" name="comment" v-model="form.note">
              </div>
            </div>
          </form>
        </div>
      </section>
      <footer class="modal-card-foot">
        <button class="button is-success" @click="saveAction">Valider</button>
        <button class="button" @click="cancelAction">Annuler</button>
      </footer>
    </div>
  </div>



</template>

<script>
    export default {
      name: "speechpart-form",
      props: ['speechpart', 'cancel', 'save'],
      data() {
        'speechpart-form data'
        return {
          form: Object.assign({}, this.speechpart),
        }
      },
      mounted () {
        console.log('speechpart-form beforeUpdate', this.speechpart)
      },
      watch: {
        speechpart: function (newSpeechpart) {
          //this.form = Object.assign({}, newSpeechpart)
        }
      },
      methods: {
        saveAction () {
          this.$props.save(this.form);
        },
        cancelAction () {
          this.$props.cancel();
        }
      }
    }
</script>
