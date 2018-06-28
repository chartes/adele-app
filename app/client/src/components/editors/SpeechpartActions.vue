<template>
    <div class="note-actions">
        <div class="field">
            <p class="control">
                <a class="button is-warning" @click="editAction">
                  <span class="icon is-small">
                    <i class="fas fa-edit"></i>
                  </span>
                    <span>Éditer la partie du discours</span>
                </a>
            </p>
        </div>
        <div class="field">
            <p class="control">
                <a class="button is-danger" @click="deleteAction">
                    <span class="icon is-small">
                        <i class="fas fa-trash"></i>
                    </span>
                    <span>Supprimer la partie du discours</span>
                </a>
            </p>
        </div>
    </div>
</template>

<script>
  export default {
    name: "note-actions",
    props: {
      edit: {
        type: Function,
        required: true
      },
      newNote: {
        type: Function,
        required: true
      },
      delete: {
        type: Function,
        required: true
      },
      updateLink: {
        type: Function,
        required: true
      },
      unlink: {
        type: Function,
        required: true
      }
    },
    methods: {
      newAction () {
        this.$props.newNote();
      },
      deleteAction () {
        this.$props.delete();
      },
      editAction () {
        this.$props.edit();
      },
      unlinkAction () {
        this.$props.unlink();
      },
      updateLinkAction () {
        this.$props.updateLink();
      }
    }
  }
</script>