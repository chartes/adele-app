<template>
    <div class="in-editor-actions">
        <div class="field">
            <p class="control">
                <a class="button" @click="editAction">
                  <span class="icon is-small">
                    <i class="fas fa-edit"></i>
                  </span>
                    <span v-text="editText"></span>
                </a>
            </p>
        </div>
        <div class="field">
            <p class="control">
                <a class="button is-danger is-outlined" @click="deleteAction">
                    <span class="icon is-small">
                        <i class="fas fa-eraser"></i>
                    </span>
                    <span v-text="deleteText">Supprimer</span>
                </a>
            </p>
        </div>
    </div>
</template>

<script>
  export default {
    name: "in-editor-actions",
    props: {
      edit : {
        type: Function,
        required: true
      },
      delete : {
        type: Function,
        required: true
      },
      editText : {
        type: String,
        default: 'Éditer'
      },
      deleteText : {
        type: String,
        default: 'Supprimer'
      }
    },
    methods: {
      deleteAction () {
        this.$props.delete();
      },
      editAction () {
        this.$props.edit();
      }
    }
  }
</script>