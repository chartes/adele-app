<template>
    <a href="#" @click.prevent="clickHandler">
        <span v-show="visible"><i class="fas fa-eye"></i></span>
        <span v-show="!visible"><i class="fas fa-eye-slash"></i></span>
        <slot></slot>
    </a>
</template>

<script>
  export default {
    name: "visibility-toggle",
    props: ['visible', 'action', 'param'],
    methods: {
      clickHandler () {
        console.log('clickHandler')
        this.action(this.param);
      }
    },
    computed: {
      iconClass () {
        return this.visible ? 'fa-eye' : 'fa-eye-slash'
      }
    }
  }
</script>

<style scoped>

</style>