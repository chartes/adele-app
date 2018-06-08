<template>

    <modal-form
            :title="title"
            :cancel="cancelAction"
            :submit="submitAction"
            :valid="form.length >= 1"
            :submittin="null"
    >
        <div class="location-form textinput-form">
            <form @submit.prevent="">
                <div class="field">
                    <label class="label">{{label}}</label>
                    <div class="control">
                        <input class="input" type="text" v-model="form">
                    </div>
                </div>
            </form>
        </div>
    </modal-form>

</template>

<script>

  import ModalForm from './ModalForm';

  export default {
    name: "textfield-form",
    components: {
      ModalForm
    },
    props: {
      title: { type: String, default: '' },
      label: { type: String, default: '' },
      value: { type: String, default: '' },
      cancel: { type: Function },
      submit: { type: Function },
    },
    data() {
      return {
        form: this.value
      }
    },
    mounted () {
    },
    methods: {

      submitAction () {
        this.$props.submit(this.form);
      },
      cancelAction () {
        this.$props.cancel();
      }
    }
  }
</script>