<template>
    <transition name="fade">
        <div class="loading-overlay" v-if="active" :class="myClasses">
            <div class="loading-background"></div>
            <div class="loading-icon"></div>
        </div>
    </transition>
</template>

<script>
  export default {
    name: "loading-indicator",
    props: {
      active: {
        type: Boolean,
        default: false
      },
      fullPage: {
        type: Boolean,
        default: false
      }
    },
    computed: {
      myClasses () {
        let classes = [];
        if (this.active) classes.push('is-active')
        if (this.fullPage) classes.push('is-full-page')
        return classes.join(' ')
      }
    }
  }
</script>

<style scoped>
    .fade-enter-active, .fade-leave-active {
        transition: opacity .25s;
    }
    .fade-enter, .fade-leave-to {
        opacity: 0;
    }
    .fade-enter-active .loading-icon, .fade-leave-active .loading-icon{
        transition: transform .25s;
    }
    .fade-enter .loading-icon, .fade-leave-to .loading-icon {
        transform: translateY(-300%);
    }
</style>