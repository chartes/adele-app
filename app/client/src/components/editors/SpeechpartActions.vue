<template>
    <div class="speechpart-actions">
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
    name: "speechpart-actions",
    props: {
      edit: {
        type: Function,
        required: true
      },
      delete: {
        type: Function,
        required: true
      },
    },
    methods: {
      deleteAction () {
        this.$props.delete();
      },
      editAction () {
        this.$props.edit();
      },
    }
  }
</script>