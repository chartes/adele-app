<template>
  <div class="speechpart-actions">
    <div class="field has-addons">
      <p class="control">
        <a class="button" @click="editAction">
                  <span class="icon is-small">
                    <i class="fas fa-edit"></i>
                  </span>
          <span>Éditer</span>
        </a>
      </p>
      <p class="control">
        <a class="button is-danger is-outlined" @click="deleteAction">
                  <span class="icon is-small">
                    <i class="fas fa-eraser"></i>
                  </span>
          <span>Supprimer</span>
        </a>
      </p>
    </div>
  </div>
</template>

<script>
    export default {
      name: "speechpart-actions",
      props: {
        edit : {
          type: Function,
          required: true
        },
        delete : {
          type: Function,
          required: true
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

<style scoped>

</style>
